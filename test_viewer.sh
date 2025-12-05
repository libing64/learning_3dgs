#!/bin/bash
# 快速测试 viewer

echo "Testing 3DGS Viewer with dummy model..."
echo ""

MODEL_PATH="test_models/dummy_model"

if [ ! -f "$MODEL_PATH/point_cloud.ply" ]; then
    echo "Test model not found. Creating one..."
    python3 create_dummy_model.py --n_points 500
fi

echo "Running viewer with test model: $MODEL_PATH"
echo "Note: This will attempt to render the model. Make sure you have:"
echo "  1. Activated conda environment: conda activate 3dgs_viewer"
echo "  2. Installed all dependencies including diff-gaussian-rasterization"
echo "  3. Have CUDA available"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

python3 viewer.py "$MODEL_PATH" --simple

