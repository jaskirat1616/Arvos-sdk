#!/usr/bin/env python3
"""
Real-time 3D point cloud viewer

Visualizes LiDAR/depth point clouds in 3D using Open3D.

Requirements:
    pip install open3d

Usage:
    python point_cloud_viewer.py
"""

import asyncio
import numpy as np
from arvos import ArvosServer, DepthFrame

try:
    import open3d as o3d
except ImportError:
    print("Error: This example requires Open3D")
    print("Install with: pip install open3d")
    exit(1)


class PointCloudVisualizer:
    def __init__(self):
        # Create visualizer
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="Arvos Point Cloud", width=1280, height=720)

        # Create point cloud object
        self.pcd = o3d.geometry.PointCloud()
        self.vis.add_geometry(self.pcd)

        # Camera setup
        view_control = self.vis.get_view_control()
        view_control.set_zoom(0.5)

        # Add coordinate frame
        coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=0.5, origin=[0, 0, 0]
        )
        self.vis.add_geometry(coordinate_frame)

        self.frame_count = 0

    def update(self, frame: DepthFrame):
        """Update point cloud with new frame"""
        self.frame_count += 1

        # Parse point cloud from PLY
        points = frame.to_point_cloud()

        if points is None or len(points) == 0:
            return

        # Extract XYZ and RGB
        xyz = points[:, :3].astype(np.float64)
        rgb = points[:, 3:6].astype(np.float64) / 255.0  # Normalize to [0, 1]

        # Update point cloud
        self.pcd.points = o3d.utility.Vector3dVector(xyz)
        self.pcd.colors = o3d.utility.Vector3dVector(rgb)

        # Update visualization
        self.vis.update_geometry(self.pcd)
        self.vis.poll_events()
        self.vis.update_renderer()

        if self.frame_count % 10 == 0:
            print(f"📊 Displayed {self.frame_count} point clouds ({len(points)} points)")

    def close(self):
        """Close visualizer"""
        self.vis.destroy_window()


async def main():
    print("🚀 Starting Arvos Point Cloud Viewer")
    print("📱 Connect your iPhone running Arvos in Mapping mode")
    print()

    # Create visualizer
    visualizer = PointCloudVisualizer()

    # Create server
    server = ArvosServer(port=9090)

    # Handle depth frames
    async def on_depth(frame: DepthFrame):
        visualizer.update(frame)

    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}")
        print("🔷 Waiting for depth data...")

    async def on_disconnect(client_id: str):
        print(f"\n❌ Client disconnected: {client_id}")
        print(f"Total point clouds displayed: {visualizer.frame_count}")

    server.on_depth = on_depth
    server.on_connect = on_connect
    server.on_disconnect = on_disconnect

    # Start server
    print("📡 Server starting...")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n👋 Closing viewer...")
        visualizer.close()


if __name__ == "__main__":
    asyncio.run(main())
