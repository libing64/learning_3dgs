#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建一个最小化的测试 3DGS 模型用于测试 viewer
"""

import numpy as np
from plyfile import PlyData, PlyElement

def create_dummy_3dgs_model(output_path="test_models/dummy_model/point_cloud.ply", n_points=1000):
    """创建一个包含基本高斯参数的测试 PLY 文件"""
    
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Creating dummy 3DGS model with {n_points} points...")
    
    # 生成随机高斯点
    xyz = np.random.randn(n_points, 3).astype(np.float32) * 0.5
    
    # Opacity (0-1)
    opacity = np.random.rand(n_points).astype(np.float32)
    opacity = 1 / (1 + np.exp(-opacity))  # sigmoid
    
    # Scale (3D)
    scale_0 = np.random.rand(n_points).astype(np.float32) * 0.01 + 0.001
    scale_1 = np.random.rand(n_points).astype(np.float32) * 0.01 + 0.001
    scale_2 = np.random.rand(n_points).astype(np.float32) * 0.01 + 0.001
    
    # Rotation (quaternion, 4D)
    rot_0 = np.random.randn(n_points).astype(np.float32) * 0.1
    rot_1 = np.random.randn(n_points).astype(np.float32) * 0.1
    rot_2 = np.random.randn(n_points).astype(np.float32) * 0.1
    rot_3 = np.random.randn(n_points).astype(np.float32) * 0.1
    # 归一化四元数
    norm = np.sqrt(rot_0**2 + rot_1**2 + rot_2**2 + rot_3**2)
    rot_0 /= norm
    rot_1 /= norm
    rot_2 /= norm
    rot_3 /= norm
    
    # SH coefficients (48 for degree 3: 3 channels * 16 coefficients)
    # 只创建基本的 SH 系数
    sh_coeffs = []
    for i in range(48):
        sh_coeffs.append(np.random.randn(n_points).astype(np.float32) * 0.1)
    
    # 创建 PLY 数据结构
    dtype = [
        ('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
        ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),  # 法向量（可选）
        ('f_dc_0', 'f4'), ('f_dc_1', 'f4'), ('f_dc_2', 'f4'),  # DC 项（RGB）
        ('opacity', 'f4'),
        ('scale_0', 'f4'), ('scale_1', 'f4'), ('scale_2', 'f4'),
        ('rot_0', 'f4'), ('rot_1', 'f4'), ('rot_2', 'f4'), ('rot_3', 'f4'),
    ]
    
    # 添加 SH 系数
    for i in range(45):  # 48 - 3 (DC) = 45
        dtype.append((f'f_rest_{i}', 'f4'))
    
    # 创建数组
    vertices = np.empty(n_points, dtype=dtype)
    vertices['x'] = xyz[:, 0]
    vertices['y'] = xyz[:, 1]
    vertices['z'] = xyz[:, 2]
    vertices['nx'] = 0.0
    vertices['ny'] = 0.0
    vertices['nz'] = 0.0
    vertices['f_dc_0'] = np.random.rand(n_points).astype(np.float32)
    vertices['f_dc_1'] = np.random.rand(n_points).astype(np.float32)
    vertices['f_dc_2'] = np.random.rand(n_points).astype(np.float32)
    vertices['opacity'] = opacity
    vertices['scale_0'] = scale_0
    vertices['scale_1'] = scale_1
    vertices['scale_2'] = scale_2
    vertices['rot_0'] = rot_0
    vertices['rot_1'] = rot_1
    vertices['rot_2'] = rot_2
    vertices['rot_3'] = rot_3
    
    for i in range(45):
        vertices[f'f_rest_{i}'] = sh_coeffs[i + 3]
    
    # 创建 PLY 元素
    el = PlyElement.describe(vertices, 'vertex')
    
    # 写入文件
    PlyData([el], text=False).write(output_path)
    
    print(f"Dummy model created at: {output_path}")
    print(f"Model contains {n_points} Gaussian points")
    print(f"\nYou can now test the viewer with:")
    print(f"  python viewer.py {os.path.dirname(output_path)}")
    print(f"  or")
    print(f"  python viewer.py {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a dummy 3DGS model for testing")
    parser.add_argument("--output", type=str, default="test_models/dummy_model/point_cloud.ply",
                       help="Output PLY file path")
    parser.add_argument("--n_points", type=int, default=1000,
                       help="Number of Gaussian points")
    
    args = parser.parse_args()
    create_dummy_3dgs_model(args.output, args.n_points)

