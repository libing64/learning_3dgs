#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 3DGS 测试模型
支持从多个源下载小型测试模型
"""

import os
import sys
import argparse
import urllib.request
import tarfile
import zipfile
from pathlib import Path

def download_file(url, output_path, description="file"):
    """下载文件并显示进度"""
    print(f"Downloading {description} from {url}...")
    try:
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size) if total_size > 0 else 0
            print(f"\rProgress: {percent:.1f}%", end='', flush=True)
        
        urllib.request.urlretrieve(url, output_path, show_progress)
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nDownload failed: {e}")
        return False

def download_from_huggingface(model_name="garden", output_dir="test_models"):
    """从 Hugging Face 下载模型（如果可用）"""
    print(f"Attempting to download {model_name} from Hugging Face...")
    # 注意：这需要根据实际的 Hugging Face 模型路径调整
    # 这里只是示例，实际使用时需要替换为真实的 URL
    print("Hugging Face download not implemented yet.")
    print("Please download manually from: https://huggingface.co/models?search=3d-gaussian-splatting")
    return False

def download_official_sample(output_dir="test_models"):
    """尝试从官方仓库下载示例数据"""
    print("Attempting to download from official 3DGS repository...")
    
    # 官方数据集的 URL（示例）
    # 实际 URL 可能需要调整
    base_url = "https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/"
    
    print("\nOfficial dataset URLs:")
    print("  Garden: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/garden.zip")
    print("  Bicycle: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/bicycle.zip")
    print("\nNote: These are training datasets, not pre-trained models.")
    print("For pre-trained models, you may need to train them yourself or find them elsewhere.")
    
    return False

def create_dummy_model(output_dir="test_models"):
    """创建虚拟测试模型"""
    print("Creating dummy test model...")
    try:
        from create_dummy_model import create_dummy_3dgs_model
        output_path = os.path.join(output_dir, "dummy_model", "point_cloud.ply")
        create_dummy_3dgs_model(output_path, n_points=1000)
        return True
    except Exception as e:
        print(f"Failed to create dummy model: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download 3DGS test models")
    parser.add_argument("--output", type=str, default="test_models",
                       help="Output directory for models")
    parser.add_argument("--model", type=str, default="dummy",
                       choices=["dummy", "garden", "bicycle"],
                       help="Model to download")
    parser.add_argument("--create-dummy", action="store_true",
                       help="Create a dummy test model")
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    if args.create_dummy or args.model == "dummy":
        success = create_dummy_model(args.output)
        if success:
            print(f"\n✓ Dummy model created successfully!")
            print(f"  Test with: python viewer.py {args.output}/dummy_model")
        else:
            print("\n✗ Failed to create dummy model")
            sys.exit(1)
    elif args.model == "garden":
        print("Garden model download not yet implemented.")
        print("Please use --create-dummy to create a test model, or download manually.")
    elif args.model == "bicycle":
        print("Bicycle model download not yet implemented.")
        print("Please use --create-dummy to create a test model, or download manually.")
    
    print("\n" + "="*60)
    print("Alternative: Download models manually from:")
    print("  1. Official repo: https://github.com/graphdeco-inria/gaussian-splatting")
    print("  2. Hugging Face: https://huggingface.co/models?search=3d-gaussian-splatting")
    print("  3. Use your own trained models")
    print("="*60)

if __name__ == "__main__":
    main()

