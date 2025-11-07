#!/usr/bin/env python3
"""
Live camera view with sensor overlay

Displays camera frames in real-time with sensor data overlay.
Includes visual representations of depth/LiDAR and GPS data.

Requirements:
    pip install opencv-python Pillow numpy

Usage:
    python live_camera_view.py
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, IMUData, PoseData, CameraFrame, DepthFrame, GPSData
from PIL import Image
import io
from datetime import datetime
import math


class LiveCameraView:
    def __init__(self):
        self.latest_frame = None
        self.latest_imu = None
        self.latest_pose = None
        self.latest_depth = None
        self.latest_gps = None
        self.frame_count = 0
        self.depth_count = 0
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

    def update_depth(self, frame: DepthFrame):
        """Update depth/LiDAR data"""
        self.latest_depth = frame
        self.depth_count += 1

    def update_gps(self, data: GPSData):
        """Update GPS data"""
        self.latest_gps = data

    def draw_depth_visualization(self, frame):
        """Draw depth point cloud as colored overlay"""
        if self.latest_depth is None:
            return frame

        height, width = frame.shape[:2]

        # Parse point cloud
        points = self.latest_depth.to_point_cloud()
        if points is None or len(points) == 0:
            return frame

        # Create depth overlay (top-right corner, 200x200)
        viz_size = 200
        depth_viz = np.zeros((viz_size, viz_size, 3), dtype=np.uint8)

        # Extract XZ coordinates (top-down view)
        xyz = points[:, :3]

        # Normalize to visualization size
        if len(xyz) > 0:
            # Use only points within reasonable range
            mask = (np.abs(xyz[:, 0]) < 3) & (np.abs(xyz[:, 2]) < 3)
            xyz_filtered = xyz[mask]

            if len(xyz_filtered) > 0:
                # Map to image coordinates
                scale = viz_size / 6.0  # 6 meters total (-3 to +3)
                x_img = ((xyz_filtered[:, 0] + 3) * scale).astype(int)
                z_img = ((xyz_filtered[:, 2] + 3) * scale).astype(int)

                # Clip to image bounds
                x_img = np.clip(x_img, 0, viz_size - 1)
                z_img = np.clip(z_img, 0, viz_size - 1)

                # Color based on depth (Y axis)
                depths = xyz_filtered[:, 1]
                colors = self._depth_to_color(depths)

                # Draw points
                for i in range(len(x_img)):
                    cv2.circle(depth_viz, (x_img[i], z_img[i]), 1, colors[i].tolist(), -1)

        # Add center marker
        cv2.circle(depth_viz, (viz_size // 2, viz_size // 2), 3, (255, 255, 255), 1)
        cv2.line(depth_viz, (viz_size // 2 - 5, viz_size // 2),
                 (viz_size // 2 + 5, viz_size // 2), (255, 255, 255), 1)
        cv2.line(depth_viz, (viz_size // 2, viz_size // 2 - 5),
                 (viz_size // 2, viz_size // 2 + 5), (255, 255, 255), 1)

        # Add border
        cv2.rectangle(depth_viz, (0, 0), (viz_size - 1, viz_size - 1), (255, 255, 255), 1)

        # Overlay on frame (top-right)
        x_offset = width - viz_size - 10
        y_offset = 10
        frame[y_offset:y_offset + viz_size, x_offset:x_offset + viz_size] = depth_viz

        # Add label
        cv2.putText(frame, "Depth/LiDAR (Top View)", (x_offset, y_offset - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def _depth_to_color(self, depths):
        """Convert depth values to colors (blue = close, red = far)"""
        # Normalize depths to 0-1
        min_d, max_d = -1.0, 1.0
        normalized = np.clip((depths - min_d) / (max_d - min_d), 0, 1)

        # Create color map (BGR)
        colors = np.zeros((len(depths), 3), dtype=np.uint8)
        colors[:, 0] = (255 * (1 - normalized)).astype(np.uint8)  # Blue (close)
        colors[:, 2] = (255 * normalized).astype(np.uint8)  # Red (far)
        colors[:, 1] = (128 * (1 - np.abs(normalized - 0.5) * 2)).astype(np.uint8)  # Green (mid)

        return colors

    def draw_gps_visualization(self, frame):
        """Draw GPS location as mini-map"""
        if self.latest_gps is None:
            return frame

        height, width = frame.shape[:2]

        # Create GPS map (bottom-right corner, 200x200)
        map_size = 200
        gps_map = np.ones((map_size, map_size, 3), dtype=np.uint8) * 40  # Dark background

        # Draw grid
        grid_spacing = map_size // 4
        for i in range(1, 4):
            cv2.line(gps_map, (i * grid_spacing, 0), (i * grid_spacing, map_size), (80, 80, 80), 1)
            cv2.line(gps_map, (0, i * grid_spacing), (map_size, i * grid_spacing), (80, 80, 80), 1)

        # Draw current position (center)
        center = (map_size // 2, map_size // 2)

        # Accuracy circle
        accuracy_pixels = min(int(self.latest_gps.horizontal_accuracy * 2), map_size // 3)
        cv2.circle(gps_map, center, accuracy_pixels, (100, 100, 0), 1)

        # Current position
        cv2.circle(gps_map, center, 5, (0, 255, 0), -1)
        cv2.circle(gps_map, center, 6, (255, 255, 255), 1)

        # Draw compass directions
        cv2.putText(gps_map, "N", (map_size // 2 - 5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(gps_map, "S", (map_size // 2 - 5, map_size - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(gps_map, "W", (5, map_size // 2 + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(gps_map, "E", (map_size - 15, map_size // 2 + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Add border
        cv2.rectangle(gps_map, (0, 0), (map_size - 1, map_size - 1), (255, 255, 255), 1)

        # Overlay on frame (bottom-right)
        x_offset = width - map_size - 10
        y_offset = height - map_size - 10
        frame[y_offset:y_offset + map_size, x_offset:x_offset + map_size] = gps_map

        # Add label
        cv2.putText(frame, "GPS Location", (x_offset, y_offset - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def draw_overlay(self, frame):
        """Draw sensor data overlay on frame"""
        if frame is None:
            return None

        # First draw visualizations
        frame = self.draw_depth_visualization(frame)
        frame = self.draw_gps_visualization(frame)

        overlay = frame.copy()
        height, width = overlay.shape[:2]

        # Semi-transparent background for text (larger for more data)
        cv2.rectangle(overlay, (10, 10), (500, 350), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        y_pos = 40

        # FPS
        cv2.putText(frame, f"Camera FPS: {self.fps:.1f}", (20, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_pos += 30

        # IMU data
        if self.latest_imu:
            acc = self.latest_imu.linear_acceleration
            gyro = self.latest_imu.angular_velocity

            cv2.putText(frame, "IMU:", (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 25
            cv2.putText(frame, f"  Accel: [{acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f}] m/s²",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20
            cv2.putText(frame, f"  Gyro:  [{gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f}] rad/s",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 30

        # Pose data
        if self.latest_pose:
            pos = self.latest_pose.position
            tracking = self.latest_pose.tracking_state

            cv2.putText(frame, "Pose:", (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 25
            cv2.putText(frame, f"  Pos: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}] m",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20

            # Tracking state with color
            state_color = (0, 255, 0) if tracking == "normal" else (0, 165, 255)
            cv2.putText(frame, f"  Tracking: {tracking}",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, state_color, 1)
            y_pos += 30

        # Depth/LiDAR data
        if self.latest_depth:
            cv2.putText(frame, "Depth/LiDAR:", (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 25
            cv2.putText(frame, f"  Points: {self.latest_depth.point_count:,}",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20
            cv2.putText(frame, f"  Range: {self.latest_depth.min_depth:.2f} - {self.latest_depth.max_depth:.2f} m",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20
            cv2.putText(frame, f"  Frames: {self.depth_count}",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 30

        # GPS data
        if self.latest_gps:
            cv2.putText(frame, "GPS:", (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 25
            cv2.putText(frame, f"  Lat: {self.latest_gps.latitude:.6f}°",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20
            cv2.putText(frame, f"  Lon: {self.latest_gps.longitude:.6f}°",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20
            cv2.putText(frame, f"  Alt: {self.latest_gps.altitude:.1f} m ±{self.latest_gps.vertical_accuracy:.1f}m",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 20
            cv2.putText(frame, f"  Accuracy: ±{self.latest_gps.horizontal_accuracy:.1f} m",
                        (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def show(self):
        """Display the frame with overlay"""
        if self.latest_frame is not None:
            display_frame = self.draw_overlay(self.latest_frame)
            cv2.imshow('Arvos Live Camera', display_frame)
        else:
            # Show placeholder if no frame yet
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for camera frames...", (100, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Arvos Live Camera', placeholder)

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
    server.on_depth = lambda frame: viewer.update_depth(frame)
    server.on_gps = lambda data: viewer.update_gps(data)

    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}")
        print("📷 Waiting for camera frames...")
        print()

    async def on_disconnect(client_id: str):
        print(f"\n❌ Client disconnected: {client_id}")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect

    # Create tasks for server and display
    async def display_loop():
        while True:
            if not viewer.show():
                break
            await asyncio.sleep(0.01)

    # Run server and display loop concurrently
    print("📡 Starting server...")

    try:
        # Run both tasks concurrently
        await asyncio.gather(
            server.start(),
            display_loop()
        )
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        print("\n👋 Camera view closed")


if __name__ == "__main__":
    asyncio.run(main())
