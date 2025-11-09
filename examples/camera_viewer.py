#!/usr/bin/env python3
"""
Camera Viewer - Dedicated camera display process

Connects to Arvos server and displays ONLY camera feed.
Part of modular ROS-like architecture.

Usage:
    python camera_viewer.py [--port 9090]
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, CameraFrame
import time
import argparse


class CameraViewer:
    def __init__(self):
        self.latest_frame = None
        self.frame_count = 0
        self.fps = 0.0
        self.last_fps_time = time.time()

    def update_camera(self, frame: CameraFrame):
        """Fast camera decode"""
        try:
            img = cv2.imdecode(np.frombuffer(frame.data, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.latest_frame = img

            self.frame_count += 1
            now = time.time()
            if now - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (now - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = now

        except Exception as e:
            print(f"❌ Decode error: {e}")


async def main():
    parser = argparse.ArgumentParser(description='Arvos Camera Viewer')
    parser.add_argument('--port', type=int, default=9090, help='Server port')
    args = parser.parse_args()

    print(f"📷 Camera Viewer")
    print(f"📡 Connecting to port {args.port}...")

    viewer = CameraViewer()
    server = ArvosServer(port=args.port)

    # Only camera callback
    server.on_camera = viewer.update_camera

    async def on_connect(client_id: str):
        print(f"✅ Connected: {client_id}")

    server.on_connect = on_connect

    # Start server
    server_task = asyncio.create_task(server.start())

    # Display loop
    running = True
    while running:
        if viewer.latest_frame is not None:
            frame = viewer.latest_frame.copy()
            # FPS overlay
            cv2.putText(frame, f"FPS: {viewer.fps:.1f}", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.imshow('Camera', frame)
        else:
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for camera...", (150, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Camera', placeholder)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            running = False
            break

        await asyncio.sleep(0)

    cv2.destroyAllWindows()
    print("👋 Camera viewer closed")


if __name__ == "__main__":
    asyncio.run(main())
