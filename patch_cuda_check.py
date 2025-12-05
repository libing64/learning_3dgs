#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时补丁：修改 PyTorch 的 CUDA 版本检查以允许安装
"""

import sys
import os

def patch_torch_cuda_check():
    """修改 PyTorch 的 CUDA 版本检查"""
    try:
        import torch
        torch_path = os.path.dirname(torch.__file__)
        cpp_ext_path = os.path.join(torch_path, 'utils', 'cpp_extension.py')
        
        if not os.path.exists(cpp_ext_path):
            print(f"Warning: {cpp_ext_path} not found")
            return False
        
        # 读取文件
        with open(cpp_ext_path, 'r') as f:
            content = f.read()
        
        # 检查是否已经修改过
        if '# PATCHED: CUDA version check disabled' in content:
            print("CUDA check already patched")
            return True
        
        # 修改 _check_cuda_version 函数
        old_check = 'def _check_cuda_version(compiler_name, compiler_version):'
        new_check = '''def _check_cuda_version(compiler_name, compiler_version):
    # PATCHED: CUDA version check disabled
    return'''
        
        if old_check in content:
            # 找到函数并替换整个函数体
            import re
            # 更简单的方法：直接注释掉检查
            pattern = r'(raise RuntimeError\(CUDA_MISMATCH_MESSAGE.*?\))'
            replacement = r'# PATCHED: Disabled CUDA version check\n        # \1'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # 备份原文件
            backup_path = cpp_ext_path + '.backup'
            if not os.path.exists(backup_path):
                with open(backup_path, 'w') as f:
                    f.write(content.replace('# PATCHED: Disabled CUDA version check\n        # ', ''))
                print(f"Backup created: {backup_path}")
            
            # 写入修改后的文件
            with open(cpp_ext_path, 'w') as f:
                f.write(content)
            print(f"Patched: {cpp_ext_path}")
            return True
        else:
            print("Could not find _check_cuda_version function")
            return False
            
    except Exception as e:
        print(f"Error patching: {e}")
        return False

if __name__ == "__main__":
    success = patch_torch_cuda_check()
    sys.exit(0 if success else 1)

