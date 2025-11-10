#!/usr/bin/env python3
"""
DepthEye-Style 3D Point Cloud Viewer

High-quality real-time 3D LiDAR/depth visualization inspired by DepthEye app.
Features heatmap coloring, confidence filtering, and smooth rendering.

Requirements:
    pip install open3d numpy

Usage:
    python deptheye_style_viewer.py [--port 9090]
"""

import asyncio
import argparse
import numpy as np
from arvos import ArvosServer, DepthFrame

try:
    import open3d as o3d
except ImportError:
    print("❌ Error: This example requires Open3D")
    print("Install with: pip install open3d")
    exit(1)


class DepthEyeViewer:
    """DepthEye-inspired 3D point cloud viewer with heatmap coloring"""

    def __init__(self):
        # Create visualizer
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="Arvos • DepthEye Style", width=1280, height=720)

        # Dark background like DepthEye
        opt = self.vis.get_render_option()
        opt.background_color = np.asarray([0.02, 0.02, 0.02])
        opt.point_size = 3.0

        # Point cloud
        self.pcd = o3d.geometry.PointCloud()
        self.vis.add_geometry(self.pcd)

        # Coordinate frame
        frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5, origin=[0, 0, 0])
        self.vis.add_geometry(frame)

        # Camera
        view_control = self.vis.get_view_control()
        view_control.set_zoom(0.5)

        self.frame_count = 0
        print("✨ DepthEye-Style Viewer Ready")

    def depth_heatmap(self, points: np.ndarray) -> np.ndarray:
        """Apply DepthEye-style depth heatmap (blue=close, red=far)"""
        depths = np.linalg.norm(points, axis=1)
        min_d, max_d = np.percentile(depths, [5, 95])
        normalized = np.clip((depths - min_d) / (max_d - min_d + 1e-6), 0, 1)

        colors = np.zeros((len(points), 3))
        for i, val in enumerate(normalized):
            if val < 0.25:
                t = val / 0.25
                colors[i] = [0, t, 1]  # Blue → Cyan
            elif val < 0.5:
                t = (val - 0.25) / 0.25
                colors[i] = [0, 1, 1 - t]  # Cyan → Green
            elif val < 0.75:
                t = (val - 0.5) / 0.25
                colors[i] = [t, 1, 0]  # Green → Yellow
            else:
                t = (val - 0.75) / 0.25
                colors[i] = [1, 1 - t, 0]  # Yellow → Red

        return colors

    def update(self, frame: DepthFrame):
        """Update point cloud"""
        self.frame_count += 1

        points_data = frame.to_point_cloud()
        if points_data is None or len(points_data) == 0:
            return

        xyz = points_data[:, :3].astype(np.float64)
        colors = self.depth_heatmap(xyz)

        self.pcd.points = o3d.utility.Vector3dVector(xyz)
        self.pcd.colors = o3d.utility.Vector3dVector(colors)

        self.vis.update_geometry(self.pcd)
        self.vis.poll_events()
        self.vis.update_renderer()

        if self.frame_count % 10 == 0:
            print(f"📊 Frame {self.frame_count}: {len(xyz):,} points")

    def close(self):
        self.vis.destroy_window()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9090)
    args = parser.parse_args()

    print("🚀 Arvos DepthEye-Style Viewer")
    print(f"📱 Connect iPhone → ws://0.0.0.0:{args.port}")
    print()

    viewer = DepthEyeViewer()
    server = ArvosServer(port=args.port)

    server.on_depth = lambda frame: viewer.update(frame)
    server.on_connect = lambda cid: print(f"✅ Connected: {cid}")
    server.on_disconnect = lambda cid: print(f"❌ Disconnected: {cid}")

    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n👋 Closing...")
    finally:
        viewer.close()


if __name__ == "__main__":
    asyncio.run(main())
