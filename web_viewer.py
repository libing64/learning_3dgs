#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3DGS Web Viewer Server
基于 gaussian-splatting-lightning 风格的 Web 查看器
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from flask import Flask, send_from_directory, send_file, jsonify, request
from flask_cors import CORS
import argparse

try:
    from plyfile import PlyData
except ImportError:
    print("Warning: plyfile not installed. Install with: pip install plyfile")
    PlyData = None

app = Flask(__name__, static_folder='web_viewer_static')
CORS(app)

# 全局变量存储模型路径
MODEL_PATH = None
MODEL_DATA = None


def load_ply_model(ply_path):
    """加载 PLY 模型并转换为 Web 可用格式"""
    if PlyData is None:
        raise RuntimeError("plyfile is required to load models")
    
    print(f"Loading model from: {ply_path}")
    plydata = PlyData.read(str(ply_path))
    
    # 提取数据
    xyz = np.stack((
        np.asarray(plydata.elements[0]["x"]),
        np.asarray(plydata.elements[0]["y"]),
        np.asarray(plydata.elements[0]["z"])
    ), axis=1).astype(np.float32)
    
    # 提取颜色（从 SH 系数或直接颜色）
    colors = None
    element = plydata.elements[0]
    # 获取属性名称列表
    property_names = [prop.name for prop in element.properties]
    
    if "f_dc_0" in property_names and "f_dc_1" in property_names and "f_dc_2" in property_names:
        # 使用 DC 项作为基础颜色
        f_dc_0 = np.asarray(element["f_dc_0"])
        f_dc_1 = np.asarray(element["f_dc_1"])
        f_dc_2 = np.asarray(element["f_dc_2"])
        # SH 到 RGB 的简单转换（DC 项）
        colors = np.stack([f_dc_0, f_dc_1, f_dc_2], axis=1)
        colors = (colors + 1) * 0.5  # 归一化到 [0, 1]
        colors = np.clip(colors, 0, 1)
    else:
        # 使用默认颜色
        colors = np.ones((xyz.shape[0], 3), dtype=np.float32) * 0.5
    
    # 提取不透明度
    if "opacity" in property_names:
        opacity = np.asarray(element["opacity"])
        opacity = 1 / (1 + np.exp(-opacity))  # sigmoid
    else:
        opacity = np.ones(xyz.shape[0], dtype=np.float32)
    
    # 提取缩放
    scale_names = [p.name for p in element.properties if p.name.startswith("scale")]
    if scale_names:
        scales = np.zeros((xyz.shape[0], len(scale_names)), dtype=np.float32)
        for idx, attr_name in enumerate(scale_names):
            scales[:, idx] = np.asarray(element[attr_name])
    else:
        scales = np.ones((xyz.shape[0], 3), dtype=np.float32) * 0.01
    
    # 提取旋转（四元数）
    rot_names = [p.name for p in element.properties if p.name.startswith("rot")]
    if rot_names:
        rotations = np.zeros((xyz.shape[0], len(rot_names)), dtype=np.float32)
        for idx, attr_name in enumerate(rot_names):
            rotations[:, idx] = np.asarray(element[attr_name])
    else:
        rotations = np.zeros((xyz.shape[0], 4), dtype=np.float32)
        rotations[:, 3] = 1.0  # w=1, 无旋转
    
    return {
        'xyz': xyz,
        'colors': colors,
        'opacity': opacity,
        'scales': scales,
        'rotations': rotations,
        'n_points': xyz.shape[0]
    }


def convert_to_web_format(model_data):
    """将模型数据转换为 Web 可用的格式"""
    # 创建适合 Web 传输的格式
    # 使用压缩的二进制格式或 JSON
    result = {
        'positions': model_data['xyz'].tolist(),
        'colors': model_data['colors'].tolist(),
        'opacities': model_data['opacity'].tolist(),
        'scales': model_data['scales'].tolist(),
        'rotations': model_data['rotations'].tolist(),
        'n_points': model_data['n_points']
    }
    return result


@app.route('/')
def index():
    """主页面"""
    html_path = Path(__file__).parent / 'web_viewer_static' / 'index.html'
    if not html_path.exists():
        return f"<h1>Error: HTML file not found at {html_path}</h1>", 404
    return send_file(str(html_path))


@app.route('/api/model')
def get_model():
    """获取模型数据"""
    global MODEL_DATA
    
    if MODEL_DATA is None:
        return jsonify({'error': 'No model loaded'}), 404
    
    # 返回模型数据
    web_data = convert_to_web_format(MODEL_DATA)
    return jsonify(web_data)


@app.route('/api/model/info')
def get_model_info():
    """获取模型信息"""
    global MODEL_DATA
    
    if MODEL_DATA is None:
        return jsonify({'error': 'No model loaded'}), 404
    
    return jsonify({
        'n_points': MODEL_DATA['n_points'],
        'bounds': {
            'min': MODEL_DATA['xyz'].min(axis=0).tolist(),
            'max': MODEL_DATA['xyz'].max(axis=0).tolist(),
            'center': MODEL_DATA['xyz'].mean(axis=0).tolist()
        }
    })


@app.route('/<path:path>')
def serve_static(path):
    """提供静态文件"""
    return send_from_directory('web_viewer_static', path)


def main():
    global MODEL_PATH, MODEL_DATA
    
    parser = argparse.ArgumentParser(description="3DGS Web Viewer")
    parser.add_argument("model_path", type=str, help="Path to 3DGS model directory or .ply file")
    parser.add_argument("--port", type=int, default=5000, help="Server port (default: 5000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    MODEL_PATH = Path(args.model_path)
    
    # 查找 PLY 文件
    if MODEL_PATH.is_file() and MODEL_PATH.suffix == ".ply":
        ply_path = MODEL_PATH
    elif MODEL_PATH.is_dir():
        # 尝试标准路径
        ply_path = MODEL_PATH / "point_cloud" / "iteration_30000" / "point_cloud.ply"
        if not ply_path.exists():
            ply_path = MODEL_PATH / "point_cloud.ply"
            if not ply_path.exists():
                # 查找任何 .ply 文件
                ply_files = list(MODEL_PATH.rglob("*.ply"))
                if ply_files:
                    ply_path = ply_files[0]
                else:
                    raise FileNotFoundError(f"Could not find .ply file in {MODEL_PATH}")
    else:
        raise FileNotFoundError(f"Model path not found: {MODEL_PATH}")
    
    print(f"Loading model: {ply_path}")
    
    # 加载模型
    try:
        MODEL_DATA = load_ply_model(ply_path)
        print(f"Model loaded: {MODEL_DATA['n_points']} points")
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 启动服务器
    print(f"\nStarting Web Viewer server...")
    print(f"Open your browser and navigate to: http://localhost:{args.port}")
    print(f"Press Ctrl+C to stop the server\n")
    
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()

