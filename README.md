# 3DGS Viewer

简易 3D Gaussian Splatting Viewer，用于查看训练好的 3DGS 模型。

## 功能特性

- 加载和可视化 3D Gaussian Splatting 模型
- 支持交互式查看（OpenGL 模式）
- 支持简单渲染模式（保存图像）
- 支持鼠标交互控制视角

## 环境要求

- Python 3.10
- CUDA 11.8+ (用于 GPU 加速)
- Conda

## 安装步骤

### 1. 创建 Conda 环境

**Linux/Mac:**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Windows:**
```cmd
setup_env.bat
```

### 2. 手动安装（如果自动脚本失败）

```bash
# 激活环境
conda activate 3dgs_viewer

# 安装 PyTorch
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 安装基础依赖
pip install -r requirements.txt

# 安装 diff-gaussian-rasterization
git clone https://github.com/graphdeco-inria/diff-gaussian-rasterization.git
cd diff-gaussian-rasterization
pip install .
cd ..

# 安装 simple-knn
git clone https://github.com/graphdeco-inria/simple-knn.git
cd simple-knn
pip install .
cd ..
```

## 使用方法

### 基本用法

```bash
# 激活环境
conda activate 3dgs_viewer

# 运行 viewer
python viewer.py <模型路径>
```

### 参数说明

- `model_path`: 3DGS 模型路径（可以是包含 `point_cloud.ply` 的目录，或直接的 `.ply` 文件路径）
- `--width`: 窗口宽度（默认: 800）
- `--height`: 窗口高度（默认: 600）
- `--simple`: 使用简单模式（不使用 OpenGL，直接保存渲染图像）

### 示例

```bash
# 查看模型（OpenGL 交互模式）
python viewer.py /path/to/your/model

# 查看模型（简单模式，保存图像）
python viewer.py /path/to/your/model --simple

# 指定窗口大小
python viewer.py /path/to/your/model --width 1920 --height 1080
```

### 模型路径格式

Viewer 支持以下模型路径格式：

1. 标准 3DGS 输出目录：
   ```
   model_path/
     └── point_cloud/
         └── iteration_30000/
             └── point_cloud.ply
   ```

2. 直接指定 ply 文件：
   ```
   python viewer.py /path/to/point_cloud.ply
   ```

## 交互控制

在 OpenGL 模式下：
- **鼠标左键拖拽**: 旋转视角
- **鼠标滚轮**: 缩放
- **ESC 或关闭窗口**: 退出

## 文件说明

- `viewer.py`: 主程序文件
- `requirements.txt`: Python 依赖包列表
- `setup_env.sh`: Linux/Mac 环境设置脚本
- `setup_env.bat`: Windows 环境设置脚本

## 注意事项

1. 确保系统已安装 CUDA 和对应的 cuDNN
2. `diff-gaussian-rasterization` 需要编译 CUDA 代码，安装可能需要较长时间
3. 如果 OpenGL 不可用，程序会自动切换到简单模式
4. 模型文件需要包含标准的 3DGS 格式数据（xyz, opacity, scale, rotation, sh_coeffs 等）

## 故障排除

### 问题：无法导入 diff-gaussian-rasterization

**解决方案**: 确保已正确安装 CUDA 开发工具，然后手动编译安装：
```bash
git clone https://github.com/graphdeco-inria/diff-gaussian-rasterization.git
cd diff-gaussian-rasterization
pip install .
```

### 问题：OpenGL 相关错误

**解决方案**: 使用 `--simple` 参数运行简单模式，或安装 OpenGL 相关库：
```bash
# Linux
sudo apt-get install libgl1-mesa-glx libglfw3

# Mac
brew install glfw
```

### 问题：CUDA out of memory

**解决方案**: 减少模型中的高斯点数量，或使用更小的窗口尺寸。

## 许可证

本项目仅供学习和研究使用。