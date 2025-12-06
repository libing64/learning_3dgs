#!/bin/bash
# 启动 Web Viewer

ENV_NAME="3dgs_viewer"
MODEL_PATH="${1:-test_models/dummy_model/point_cloud.ply}"
PORT="${2:-5000}"

echo "Starting 3DGS Web Viewer..."
echo "Model: $MODEL_PATH"
echo "Port: $PORT"
echo ""

# 检查模型文件
if [ ! -f "$MODEL_PATH" ] && [ ! -d "$MODEL_PATH" ]; then
    echo "Error: Model path not found: $MODEL_PATH"
    echo ""
    echo "Usage: $0 [model_path] [port]"
    echo "Example: $0 test_models/dummy_model/point_cloud.ply 5000"
    exit 1
fi

# 激活环境并启动服务器
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

echo "Starting server..."
echo "Open your browser at: http://localhost:$PORT"
echo "Press Ctrl+C to stop"
echo ""

python web_viewer.py "$MODEL_PATH" --port "$PORT"

