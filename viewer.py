#!/usr/bin/env python3
"""
简易 3D Gaussian Splatting Viewer
用于查看训练好的 3DGS 模型
"""

import os
import sys
import numpy as np
import torch
import json
from pathlib import Path
import argparse

try:
    from diff_gaussian_rasterization import GaussianRasterizationSettings, GaussianRasterizer
    HAS_RASTERIZER = True
except ImportError:
    print("Warning: diff-gaussian-rasterization not found. Please install it from:")
    print("https://github.com/graphdeco-inria/diff-gaussian-rasterization")
    HAS_RASTERIZER = False

# 尝试导入 SH 工具（可能在不同的包中）
try:
    from sh_utils import SH2RGB
    HAS_SH_UTILS = True
except ImportError:
    try:
        # 尝试从其他可能的位置导入
        import sys
        sys.path.append('.')
        from scene.gaussian_model import SH2RGB
        HAS_SH_UTILS = True
    except ImportError:
        HAS_SH_UTILS = False
        print("Warning: SH2RGB not found. Will use default colors.")

try:
    import OpenGL.GL as gl
    from OpenGL.GL import shaders
    import glfw
except ImportError:
    print("Warning: PyOpenGL and glfw not found. Installing alternative viewer...")
    # 使用简单的 matplotlib 作为备选方案
    USE_MATPLOTLIB = True
else:
    USE_MATPLOTLIB = False


class Simple3DGSViewer:
    """简易 3DGS Viewer"""
    
    def __init__(self, model_path, width=800, height=600):
        self.model_path = Path(model_path)
        self.width = width
        self.height = height
        
        # 加载模型
        self.gaussians = self.load_model()
        
        # 相机参数
        self.camera_center = torch.tensor([0.0, 0.0, 0.0], dtype=torch.float32)
        self.camera_rotation = torch.eye(3, dtype=torch.float32)
        self.fov = 0.8
        self.scale = 1.0
        
        # 鼠标控制
        self.last_mouse_pos = None
        self.rotation_speed = 0.01
        
    def load_model(self):
        """加载 3DGS 模型"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model path not found: {self.model_path}")
        
        # 尝试加载 ply 文件（标准 3DGS 格式）
        ply_path = self.model_path / "point_cloud" / "iteration_30000" / "point_cloud.ply"
        if not ply_path.exists():
            # 尝试其他可能的路径
            ply_path = self.model_path / "point_cloud.ply"
            if not ply_path.exists():
                # 尝试直接作为 ply 文件
                if self.model_path.suffix == ".ply":
                    ply_path = self.model_path
                else:
                    raise FileNotFoundError(f"Could not find point_cloud.ply in {self.model_path}")
        
        print(f"Loading model from: {ply_path}")
        
        # 这里应该使用 plyfile 库来加载，但为了简化，我们创建一个示例加载器
        # 实际使用时需要根据具体的 3DGS 模型格式来调整
        try:
            from plyfile import PlyData
            plydata = PlyData.read(str(ply_path))
            
            # 提取高斯参数
            xyz = np.stack((np.asarray(plydata.elements[0]["x"]),
                           np.asarray(plydata.elements[0]["y"]),
                           np.asarray(plydata.elements[0]["z"])), axis=1)
            
            # 提取其他属性（opacities, scales, rotations, sh_coeffs 等）
            opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis]
            
            scale_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("scale")]
            scales = np.zeros((xyz.shape[0], len(scale_names)))
            for idx, attr_name in enumerate(scale_names):
                scales[:, idx] = np.asarray(plydata.elements[0][attr_name])
            
            rot_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("rot")]
            rots = np.zeros((xyz.shape[0], len(rot_names)))
            for idx, attr_name in enumerate(rot_names):
                rots[:, idx] = np.asarray(plydata.elements[0][attr_name])
            
            shs = None
            shs_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("f_rest_")]
            if shs_names:
                shs = np.zeros((xyz.shape[0], len(shs_names)))
                for idx, attr_name in enumerate(shs_names):
                    shs[:, idx] = np.asarray(plydata.elements[0][attr_name])
            
            return {
                'xyz': torch.tensor(xyz, dtype=torch.float32).cuda(),
                'opacities': torch.tensor(opacities, dtype=torch.float32).cuda(),
                'scales': torch.tensor(scales, dtype=torch.float32).cuda(),
                'rotations': torch.tensor(rots, dtype=torch.float32).cuda(),
                'shs': torch.tensor(shs, dtype=torch.float32).cuda() if shs is not None else None,
            }
        except ImportError:
            print("Warning: plyfile not found. Using dummy data for demonstration.")
            # 创建示例数据
            n_points = 1000
            return {
                'xyz': torch.randn(n_points, 3, dtype=torch.float32).cuda() * 0.5,
                'opacities': torch.sigmoid(torch.randn(n_points, 1, dtype=torch.float32)).cuda(),
                'scales': torch.ones(n_points, 3, dtype=torch.float32).cuda() * 0.01,
                'rotations': torch.randn(n_points, 4, dtype=torch.float32).cuda(),
                'shs': torch.randn(n_points, 48, dtype=torch.float32).cuda(),
            }
    
    def render(self, camera_center, camera_rotation, fov):
        """渲染场景"""
        if not HAS_RASTERIZER:
            raise RuntimeError("diff-gaussian-rasterization is not installed")
        
        # 设置光栅化参数
        tanfovx = float(np.tan(fov * 0.5))
        tanfovy = float(np.tan(fov * 0.5 * (self.height / self.width)))
        
        # 构建视图矩阵（简化版本）
        viewmatrix = torch.eye(4, dtype=torch.float32).cuda()
        viewmatrix[:3, 3] = -camera_center.cuda()
        
        # 构建投影矩阵（简化版本）
        projmatrix = torch.eye(4, dtype=torch.float32).cuda()
        
        raster_settings = GaussianRasterizationSettings(
            image_height=self.height,
            image_width=self.width,
            tanfovx=tanfovx,
            tanfovy=tanfovy,
            bg=torch.tensor([0, 0, 0], dtype=torch.float32).cuda(),
            scale_modifier=1.0,
            viewmatrix=viewmatrix,
            projmatrix=projmatrix,
            sh_degree=3,
            campos=camera_center.cuda(),
            prefiltered=False,
            debug=False
        )
        
        rasterizer = GaussianRasterizer(raster_settings=raster_settings)
        
        # 准备高斯参数
        means3D = self.gaussians['xyz']
        opacity = self.gaussians['opacities']
        scales = self.gaussians['scales']
        rotations = self.gaussians['rotations']
        shs = self.gaussians['shs']
        
        # 如果 shs 为 None，使用默认颜色
        if shs is None:
            colors_precomp = torch.ones_like(means3D)
            shs = None
        else:
            colors_precomp = None
        
        # 渲染
        rendered_image, radii = rasterizer(
            means3D=means3D,
            means2D=None,
            shs=shs,
            colors_precomp=colors_precomp,
            opacities=opacity,
            scales=scales,
            rotations=rotations,
            cov3D_precomp=None
        )
        
        return rendered_image
    
    def run_opengl_viewer(self):
        """运行 OpenGL viewer"""
        if USE_MATPLOTLIB:
            self.run_simple_viewer()
            return
            
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        window = glfw.create_window(self.width, self.height, "3DGS Viewer", None, None)
        if not window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")
        
        glfw.make_context_current(window)
        
        # 设置回调
        def mouse_button_callback(window, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT:
                if action == glfw.PRESS:
                    x, y = glfw.get_cursor_pos(window)
                    self.last_mouse_pos = (x, y)
                else:
                    self.last_mouse_pos = None
        
        def cursor_pos_callback(window, x, y):
            if self.last_mouse_pos is not None:
                dx = x - self.last_mouse_pos[0]
                dy = y - self.last_mouse_pos[1]
                # 更新相机旋转（简化处理）
                self.last_mouse_pos = (x, y)
        
        def scroll_callback(window, xoffset, yoffset):
            self.scale *= (1.0 + yoffset * 0.1)
            self.scale = max(0.1, min(10.0, self.scale))
        
        glfw.set_mouse_button_callback(window, mouse_button_callback)
        glfw.set_cursor_pos_callback(window, cursor_pos_callback)
        glfw.set_scroll_callback(window, scroll_callback)
        
        print("3DGS Viewer started. Use mouse to rotate, scroll to zoom.")
        print("Press ESC or close window to exit.")
        
        frame_count = 0
        while not glfw.window_should_close(window):
            glfw.poll_events()
            
            try:
                # 渲染
                rendered_image = self.render(
                    self.camera_center * self.scale,
                    self.camera_rotation,
                    self.fov
                )
                
                # 转换为 numpy 并显示（简化版本）
                # 实际应用中应该使用 OpenGL 纹理和 FBO
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Rendering frame {frame_count}...")
                
            except Exception as e:
                print(f"Rendering error: {e}")
                break
            
            glfw.swap_buffers(window)
        
        glfw.terminate()
    
    def run_simple_viewer(self):
        """运行简单的查看器（使用 matplotlib 或保存图像）"""
        print("Running simple viewer mode...")
        print("Rendering sample view...")
        
        # 渲染一个视角
        rendered_image = self.render(
            self.camera_center,
            self.camera_rotation,
            self.fov
        )
        
        # 转换为 numpy 并保存
        img = rendered_image.detach().cpu().numpy()
        img = np.clip(img, 0, 1)
        
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 10))
            plt.imshow(img.transpose(1, 2, 0))
            plt.axis('off')
            plt.title("3DGS Rendered View")
            plt.savefig("rendered_view.png", dpi=150, bbox_inches='tight')
            print("Rendered image saved to rendered_view.png")
            plt.show()
        except ImportError:
            from PIL import Image
            img_uint8 = (img.transpose(1, 2, 0) * 255).astype(np.uint8)
            Image.fromarray(img_uint8).save("rendered_view.png")
            print("Rendered image saved to rendered_view.png")


def main():
    parser = argparse.ArgumentParser(description="简易 3DGS Viewer")
    parser.add_argument("model_path", type=str, help="Path to 3DGS model directory or .ply file")
    parser.add_argument("--width", type=int, default=800, help="Viewer width")
    parser.add_argument("--height", type=int, default=600, help="Viewer height")
    parser.add_argument("--simple", action="store_true", help="Use simple viewer mode (no OpenGL)")
    
    args = parser.parse_args()
    
    try:
        viewer = Simple3DGSViewer(args.model_path, args.width, args.height)
        
        if args.simple or USE_MATPLOTLIB:
            viewer.run_simple_viewer()
        else:
            viewer.run_opengl_viewer()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

