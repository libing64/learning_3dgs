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

## 获取测试模型

### 方法1: 创建虚拟测试模型（快速测试）

```bash
# 创建一个包含 1000 个高斯点的测试模型
python create_dummy_model.py

# 或者使用下载脚本
python download_model.py --create-dummy
```

这会在 `test_models/dummy_model/point_cloud.ply` 创建一个测试模型。

### 方法2: 从官方源下载

```bash
# 查看下载选项
python download_model.py --help

# 或查看说明
./download_test_model.sh
```

### 方法3: 使用自己的训练模型

如果您已经训练了 3DGS 模型，可以直接使用。

## 安装 diff-gaussian-rasterization

**重要**: viewer 需要 `diff-gaussian-rasterization` 库才能运行。安装方法：

```bash
# 方法1: 使用安装脚本（推荐，会自动处理 CUDA 版本问题）
./install_rasterizer.sh

# 方法2: 手动安装
conda activate 3dgs_viewer

# 先安装 simple-knn (依赖)
git clone https://github.com/graphdeco-inria/simple-knn.git
cd simple-knn
pip install . --no-build-isolation
cd ..

# 安装 diff-gaussian-rasterization
git clone --recursive https://github.com/graphdeco-inria/diff-gaussian-rasterization.git
cd diff-gaussian-rasterization
pip install . --no-build-isolation
cd ..
```

**注意**: 如果遇到 CUDA 版本不匹配错误（如 "CUDA version mismatches"），安装脚本会自动应用补丁。如果手动安装，可能需要：
1. 使用 `--no-build-isolation` 标志
2. 或者运行 `python patch_cuda_check.py` 来临时禁用 CUDA 版本检查

## 使用方法

### 基本用法

**重要**: 确保正确激活 conda 环境：

```bash
# 激活环境（必须）
conda activate 3dgs_viewer

# 验证 Python 路径
which python
# 应该显示: /path/to/conda/envs/3dgs_viewer/bin/python

# 运行 viewer（使用测试模型）
python viewer.py test_models/dummy_model

# 或使用自己的模型
python viewer.py <模型路径>
```

**如果环境没有正确激活**，可以使用：

```bash
# 使用 conda run 直接运行（无需手动激活）
conda run -n 3dgs_viewer python viewer.py test_models/dummy_model --simple
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

## Web Viewer

项目还包含一个基于 Web 的查看器，可以在浏览器中交互式查看 3DGS 模型。

### 启动 Web Viewer

```bash
# 激活环境
conda activate 3dgs_viewer

# 启动 Web 服务器
python web_viewer.py <模型路径> [--port 5000]

# 例如
python web_viewer.py test_models/dummy_model/point_cloud.ply
```

然后在浏览器中打开 `http://localhost:5000` 即可查看模型。

### Web Viewer 功能

- **交互式查看**: 使用鼠标拖拽旋转、滚轮缩放
- **实时控制**: 调整点大小、透明度、背景色
- **性能监控**: 显示 FPS 和模型信息
- **响应式设计**: 适配不同屏幕尺寸

### Web Viewer 参数

- `model_path`: 3DGS 模型路径（目录或 .ply 文件）
- `--port`: 服务器端口（默认: 5000）
- `--host`: 服务器主机（默认: 0.0.0.0）

## 文件说明

- `viewer.py`: 命令行查看器主程序
- `web_viewer.py`: Web 查看器服务器
- `web_viewer_static/`: Web 前端文件目录
- `requirements.txt`: Python 依赖包列表
- `setup_env.sh`: Linux/Mac 环境设置脚本
- `install_rasterizer.sh`: 安装 rasterizer 的脚本

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



# 3dgs存储格式

在3D Gaussian Splatting (3DGS) 技术中，模型的存储格式是连接训练与部署的关键环节。目前核心的存储方案是扩展的PLY格式，同时，为了满足不同应用场景对效率和标准化的需求，也出现了如专用二进制格式和正在标准化的glTF扩展等方案。

下表为您梳理了这几种主要的存储格式及其核心特点，方便您快速对比。

格式类型 主要特点 文件扩展名 适用场景

扩展PLY格式 通用，可读性好，包含全部高斯参数（位置、颜色、球谐系数等） .ply 模型交换、归档、多数框架的默认输出

专用二进制格式 加载速度快，存储体积小，通常为特定框架优化 .splat, .ksplat 高性能实时渲染、Web应用

glTF扩展(发展中) 遵循开放标准，易于集成到现代3D应用和引擎中 .gltf, .glb 未来在Web、AR/VR应用中的统一交付格式

⚙️ 核心格式深度解析

## 扩展PLY格式

这是目前最常用、最通用的3DGS模型存储格式。它在传统PLY格式的基础上，定义了一套专门的属性来存储高斯分布的所有参数。

• 属性定义：在官方实现中，construct_list_of_attributes 方法定义了包含多达23个属性的扩展集：

  • 几何基础：x, y, z（空间坐标）和占位用的 nx, ny, nz（法向量，实际未使用）。

  • 外观特征：f_dc_*（球谐函数的DC分量，控制基础颜色）和 f_rest_*（球谐函数的高阶分量，控制视角相关的细节如镜面反射）。

  • 形态与透明度：scale_*（缩放因子，决定高斯椭球的形状大小）、rot_*（旋转四元数，决定高斯椭球的方向）和 opacity（不透明度）。

• 关键设计：文件存储的是参数的原始优化值（例如缩放因子存储的是指数计算前的值），而不是经过激活函数（如Sigmoid、指数函数）处理后的最终值。这样设计是为了保证模型被加载后，可以直接继续投入训练。

```
ply
format binary_little_endian 1.0
element vertex 500
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
property float f_rest_0
property float f_rest_1
property float f_rest_2
property float f_rest_3
property float f_rest_4
property float f_rest_5
property float f_rest_6
property float f_rest_7
property float f_rest_8
property float f_rest_9
property float f_rest_10
property float f_rest_11
property float f_rest_12
property float f_rest_13
property float f_rest_14
property float f_rest_15
property float f_rest_16
property float f_rest_17
property float f_rest_18
property float f_rest_19
property float f_rest_20
property float f_rest_21
property float f_rest_22
property float f_rest_23
property float f_rest_24
property float f_rest_25
property float f_rest_26
property float f_rest_27
property float f_rest_28
property float f_rest_29
property float f_rest_30
property float f_rest_31
property float f_rest_32
property float f_rest_33
property float f_rest_34
property float f_rest_35
property float f_rest_36
property float f_rest_37
property float f_rest_38
property float f_rest_39
property float f_rest_40
property float f_rest_41
property float f_rest_42
property float f_rest_43
property float f_rest_44
end_header
```
