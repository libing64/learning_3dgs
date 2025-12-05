#!/bin/bash
# 下载小型 3DGS 测试模型

MODEL_DIR="test_models"
MODEL_NAME="garden"

echo "Downloading test 3DGS model..."

# 创建模型目录
mkdir -p $MODEL_DIR

# 方法1: 从官方仓库下载（如果可用）
# 注意：这需要根据实际的模型存储位置调整
echo "Attempting to download from official sources..."

# 尝试从 Hugging Face 或其他公开源下载
# 这里使用一个示例 URL，实际使用时需要替换为真实的下载链接

# 方法2: 使用 wget 或 curl 下载（示例）
# 由于没有直接的公开下载链接，我们创建一个说明文件

cat > $MODEL_DIR/README.md << 'EOF'
# 测试模型下载说明

## 方法1: 从官方 3DGS 仓库下载

1. 访问官方仓库: https://github.com/graphdeco-inria/gaussian-splatting
2. 下载示例数据，例如：
   - Garden scene
   - Bicycle scene
   - 或其他小型场景

## 方法2: 使用预训练模型

可以从以下来源获取小型测试模型：

1. **Hugging Face**: 搜索 "3d-gaussian-splatting"
2. **官方数据**: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/
3. **其他公开数据集**

## 模型结构要求

下载的模型应该包含以下结构之一：

```
model_path/
  └── point_cloud/
      └── iteration_30000/
          └── point_cloud.ply
```

或者直接是：

```
point_cloud.ply
```

## 快速测试

如果您已经有一个训练好的模型，可以直接使用：

```bash
python viewer.py <your_model_path>
```

如果没有模型，可以：
1. 使用自己的数据训练一个模型
2. 从上述来源下载一个示例模型
EOF

echo ""
echo "由于没有直接的公开下载链接，已创建说明文件: $MODEL_DIR/README.md"
echo ""
echo "您可以通过以下方式获取测试模型："
echo "1. 从官方仓库下载示例数据"
echo "2. 使用自己的训练数据"
echo "3. 从 Hugging Face 等平台下载预训练模型"
echo ""
echo "或者，我可以帮您创建一个最小化的测试 PLY 文件用于验证 viewer 功能。"

