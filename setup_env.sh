#!/bin/bash
# 创建 conda 环境并安装依赖

ENV_NAME="3dgs_viewer"
PYTHON_VERSION="3.10"

echo "Creating conda environment: $ENV_NAME with Python $PYTHON_VERSION"

# 创建 conda 环境
conda create -n $ENV_NAME python=$PYTHON_VERSION -y

# 激活环境
echo "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# 安装 PyTorch (CUDA 版本，根据系统调整)
echo "Installing PyTorch..."
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

# 安装其他依赖
echo "Installing other dependencies..."
pip install -r requirements.txt

# 安装 diff-gaussian-rasterization
echo "Installing diff-gaussian-rasterization..."
echo "Note: This may take a while as it needs to compile CUDA code..."

# 尝试从 pip 安装（如果可用）
pip install diff-gaussian-rasterization || {
    echo "pip install failed, trying to install from source..."
    if [ -d "diff-gaussian-rasterization" ]; then
        cd diff-gaussian-rasterization
        pip install .
        cd ..
    else
        echo "Cloning diff-gaussian-rasterization repository..."
        git clone https://github.com/graphdeco-inria/diff-gaussian-rasterization.git
        cd diff-gaussian-rasterization
        pip install .
        cd ..
    fi
}

# 安装 simple-knn (依赖)
echo "Installing simple-knn..."
pip install simple-knn || {
    echo "pip install failed, trying to install from source..."
    if [ -d "simple-knn" ]; then
        cd simple-knn
        pip install .
        cd ..
    else
        echo "Cloning simple-knn repository..."
        git clone https://github.com/graphdeco-inria/simple-knn.git
        cd simple-knn
        pip install .
        cd ..
    fi
}

echo ""
echo "Environment setup complete!"
echo "To activate the environment, run:"
echo "  conda activate $ENV_NAME"
echo ""
echo "To use the viewer, run:"
echo "  python viewer.py <path_to_model>"

