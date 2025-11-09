#!/usr/bin/env python3
"""
Depth Viewer - Dedicated depth/LiDAR display process

Connects to Arvos server and displays ONLY depth data.
Part of modular ROS-like architecture.

Usage:
    python depth_viewer.py [--port 9090]
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, DepthFrame
import argparse


class DepthViewer:
    def __init__(self):
        self.latest_depth = None
        self.depth_count = 0

    def update_depth(self, frame: DepthFrame):
        """Store depth data"""
        self.latest_depth = frame
        self.depth_count += 1
        if self.depth_count % 10 == 0:
            print(f"🔵 Depth #{self.depth_count}: {frame.point_count} points")

    def render(self):
        """Render depth map"""
        if self.latest_depth is None or self.latest_depth.point_count == 0:
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for depth...", (150, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Depth', placeholder)
            return

        try:
            points = self.latest_depth.to_point_cloud()
            if points is None or len(points) == 0:
                return

            xyz = points[:, :3] if points.shape[1] >= 3 else None
            if xyz is None:
                return

            # Filter NaN/inf
            valid = np.all(np.isfinite(xyz), axis=1)
            xyz = xyz[valid]
            if len(xyz) == 0:
                return

            # Fast vectorized projection
            x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]

            W, H = 640, 480
            depth_img = np.zeros((H, W), dtype=np.float32)
            count_img = np.zeros((H, W), dtype=np.int32)

            # Project (clip to avoid overflow)
            img_x = np.clip(((x + 2.0) / 4.0 * W).astype(int), 0, W-1)
            img_y = np.clip(((z + 2.0) / 4.0 * H).astype(int), 0, H-1)
            depths = np.abs(y)

            np.add.at(depth_img, (img_y, img_x), depths)
            np.add.at(count_img, (img_y, img_x), 1)

            mask = count_img > 0
            depth_img[mask] /= count_img[mask]

            # Normalize and colorize
            if depth_img.max() > 0:
                depth_norm = np.clip(depth_img / depth_img.max(), 0, 1)
            else:
                depth_norm = depth_img

            depth_colored = cv2.applyColorMap((depth_norm * 255).astype(np.uint8), cv2.COLORMAP_JET)
            depth_colored[~mask] = [0, 0, 0]

            # Info overlay
            cv2.putText(depth_colored, f"Points: {len(xyz):,}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(depth_colored, f"Range: {self.latest_depth.min_depth:.2f}-{self.latest_depth.max_depth:.2f}m",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow('Depth', depth_colored)

        except Exception as e:
            print(f"❌ Depth error: {e}")


async def main():
    parser = argparse.ArgumentParser(description='Arvos Depth Viewer')
    parser.add_argument('--port', type=int, default=9090, help='Server port')
    args = parser.parse_args()

    print(f"🔵 Depth Viewer")
    print(f"📡 Connecting to port {args.port}...")

    viewer = DepthViewer()
    server = ArvosServer(port=args.port)

    # Only depth callback
    server.on_depth = viewer.update_depth

    async def on_connect(client_id: str):
        print(f"✅ Connected: {client_id}")

    server.on_connect = on_connect

    # Start server
    server_task = asyncio.create_task(server.start())

    # Display loop
    running = True
    while running:
        viewer.render()

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            running = False
            break

        await asyncio.sleep(0)

    cv2.destroyAllWindows()
    print("👋 Depth viewer closed")


if __name__ == "__main__":
    asyncio.run(main())
