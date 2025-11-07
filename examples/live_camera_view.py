#!/usr/bin/env python3
"""
Live camera view with sensor overlay

Displays camera frames in real-time with sensor data overlay.

Requirements:
    pip install opencv-python Pillow numpy

Usage:
    python live_camera_view.py
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, IMUData, PoseData, CameraFrame
from PIL import Image
import io
from datetime import datetime


class LiveCameraView:
    def __init__(self):
        self.latest_frame = None
        self.latest_imu = None
        self.latest_pose = None
        self.frame_count = 0
        self.fps = 0
        self.last_time = datetime.now()

    def update_camera(self, frame: CameraFrame):
        """Update camera frame"""
        # Decode JPEG
        try:
            image = Image.open(io.BytesIO(frame.data))
            img_array = np.array(image)

            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            self.latest_frame = img_bgr
            self.frame_count += 1

            # Calculate FPS
            now = datetime.now()
            elapsed = (now - self.last_time).total_seconds()
            if elapsed > 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.last_time = now

        except Exception as e:
            print(f"Failed to decode frame: {e}")

    def update_imu(self, data: IMUData):
        """Update IMU data"""
        self.latest_imu = data

    def update_pose(self, data: PoseData):
        """Update pose data"""
        self.latest_pose = data

    def draw_overlay(self, frame):
        """Draw sensor data overlay on frame"""
        if frame is None:
            return None

        overlay = frame.copy()
        height, width = overlay.shape[:2]

        # Semi-transparent background for text
        cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # IMU data
        if self.latest_imu:
            acc = self.latest_imu.linear_acceleration
            gyro = self.latest_imu.angular_velocity

            cv2.putText(frame, "IMU:", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"  Accel: [{acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f}] m/s²",
                        (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"  Gyro:  [{gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f}] rad/s",
                        (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Pose data
        if self.latest_pose:
            pos = self.latest_pose.position
            tracking = self.latest_pose.tracking_state

            cv2.putText(frame, "Pose:", (20, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"  Pos: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}] m",
                        (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Tracking state with color
            state_color = (0, 255, 0) if tracking == "normal" else (0, 165, 255)
            cv2.putText(frame, f"  Tracking: {tracking}",
                        (20, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5, state_color, 1)

        return frame

    def show(self):
        """Display the frame with overlay"""
        if self.latest_frame is not None:
            display_frame = self.draw_overlay(self.latest_frame)
            cv2.imshow('Arvos Live Camera', display_frame)

            # Process events
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                return False

        return True


async def main():
    print("🚀 Starting Arvos Live Camera View")
    print("📱 Connect your iPhone running Arvos")
    print("Press 'q' to quit\n")

    # Create viewer
    viewer = LiveCameraView()

    # Create server
    server = ArvosServer(port=9090)

    # Set up callbacks
    server.on_camera = lambda frame: viewer.update_camera(frame)
    server.on_imu = lambda data: viewer.update_imu(data)
    server.on_pose = lambda data: viewer.update_pose(data)

    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}")
        print("📷 Waiting for camera frames...")
        print()

    async def on_disconnect(client_id: str):
        print(f"\n❌ Client disconnected: {client_id}")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect

    # Run server in background
    import threading

    def run_server():
        asyncio.run(server.start())

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Display loop
    print("📡 Server started. Waiting for connection...")

    try:
        while True:
            if not viewer.show():
                break
            await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        print("\n👋 Camera view closed")


if __name__ == "__main__":
    asyncio.run(main())
