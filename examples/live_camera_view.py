#!/usr/bin/env python3
"""
Live camera view with sensor overlay

Displays camera frames in real-time with sensor data overlay.
Includes visual representations of depth/LiDAR and GPS data in separate windows.

Requirements:
    pip install opencv-python Pillow numpy requests

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
import requests
from io import BytesIO


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

        # GPS map cache
        self.gps_map_cache = None
        self.last_gps_update = None

        # Window names
        self.camera_window = 'Arvos - Camera Feed'
        self.depth_window = 'Arvos - Depth/LiDAR'
        self.gps_window = 'Arvos - GPS Map'

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
            print(f"❌ Failed to decode frame: {e}")

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
        if self.depth_count <= 3 or self.depth_count % 10 == 0:
            print(f"🔵 Depth frame #{self.depth_count}: {frame.point_count} points, range: {frame.min_depth:.2f}-{frame.max_depth:.2f}m")

    def update_gps(self, data: GPSData):
        """Update GPS data"""
        self.latest_gps = data
        # GPS updates slowly, print all of them
        print(f"🌍 GPS: ({data.latitude:.6f}, {data.longitude:.6f}), ±{data.horizontal_accuracy:.1f}m")

    def show_depth_window(self):
        """Display depth/LiDAR visualization in separate window"""
        if self.latest_depth is None:
            # Show placeholder
            placeholder = np.zeros((600, 800, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for depth data...", (250, 300),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(self.depth_window, placeholder)
            return

        # Parse point cloud
        try:
            points = self.latest_depth.to_point_cloud()
            if points is None or len(points) == 0:
                return
        except Exception as e:
            print(f"❌ Error parsing point cloud: {e}")
            return

        # Create larger depth visualization (800x600)
        viz_width, viz_height = 800, 600
        depth_viz = np.zeros((viz_height, viz_width, 3), dtype=np.uint8)

        # Extract XZ coordinates (top-down view)
        xyz = points[:, :3]

        # Normalize to visualization size
        if len(xyz) > 0:
            # Use only points within reasonable range
            max_range = 5.0  # 5 meters
            mask = (np.abs(xyz[:, 0]) < max_range) & (np.abs(xyz[:, 2]) < max_range)
            xyz_filtered = xyz[mask]

            if len(xyz_filtered) > 0:
                # Map to image coordinates
                scale_x = viz_width / (2 * max_range)
                scale_z = viz_height / (2 * max_range)
                x_img = ((xyz_filtered[:, 0] + max_range) * scale_x).astype(int)
                z_img = ((xyz_filtered[:, 2] + max_range) * scale_z).astype(int)

                # Clip to image bounds
                x_img = np.clip(x_img, 0, viz_width - 1)
                z_img = np.clip(z_img, 0, viz_height - 1)

                # Color based on depth (Y axis)
                depths = xyz_filtered[:, 1]
                colors = self._depth_to_color(depths)

                # Draw points (larger size for visibility)
                for i in range(len(x_img)):
                    cv2.circle(depth_viz, (x_img[i], z_img[i]), 2, colors[i].tolist(), -1)

        # Add grid lines
        for i in range(0, viz_width, viz_width // 10):
            cv2.line(depth_viz, (i, 0), (i, viz_height), (50, 50, 50), 1)
        for i in range(0, viz_height, viz_height // 10):
            cv2.line(depth_viz, (0, i), (viz_width, i), (50, 50, 50), 1)

        # Add center marker (device position)
        center_x, center_y = viz_width // 2, viz_height // 2
        cv2.circle(depth_viz, (center_x, center_y), 8, (0, 255, 0), -1)
        cv2.circle(depth_viz, (center_x, center_y), 10, (255, 255, 255), 2)

        # Add distance markers
        for dist in [1, 2, 3, 4, 5]:
            radius = int(dist * scale_z)
            cv2.circle(depth_viz, (center_x, center_y), radius, (100, 100, 100), 1)
            cv2.putText(depth_viz, f"{dist}m", (center_x + radius + 5, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        # Add labels
        cv2.putText(depth_viz, f"Points: {len(xyz_filtered if len(xyz) > 0 else [])} / {len(xyz)}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(depth_viz, f"Range: {self.latest_depth.min_depth:.2f}m - {self.latest_depth.max_depth:.2f}m",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(depth_viz, "Top-down view (device at center)", (10, viz_height - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow(self.depth_window, depth_viz)

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

    def show_gps_window(self):
        """Display GPS location with real map in separate window"""
        if self.latest_gps is None:
            # Show placeholder
            placeholder = np.zeros((600, 800, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for GPS data...", (250, 300),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(self.gps_window, placeholder)
            return

        # Fetch OpenStreetMap tile
        try:
            lat = self.latest_gps.latitude
            lon = self.latest_gps.longitude
            zoom = 17  # Street-level view

            # Download map tile from OpenStreetMap
            map_img = self._get_osm_map(lat, lon, zoom, width=800, height=600)

            if map_img is not None:
                # Add marker for current position
                center_x, center_y = 400, 300

                # Draw accuracy circle
                meters_per_pixel = 156543.03392 * math.cos(lat * math.pi / 180) / (2 ** zoom)
                accuracy_pixels = int(self.latest_gps.horizontal_accuracy / meters_per_pixel)
                accuracy_pixels = min(accuracy_pixels, 200)  # Cap at 200 pixels

                cv2.circle(map_img, (center_x, center_y), accuracy_pixels, (100, 100, 255), 2)

                # Draw position marker
                cv2.circle(map_img, (center_x, center_y), 10, (0, 0, 255), -1)
                cv2.circle(map_img, (center_x, center_y), 12, (255, 255, 255), 2)

                # Add GPS info overlay
                overlay = map_img.copy()
                cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
                map_img = cv2.addWeighted(overlay, 0.6, map_img, 0.4, 0)

                cv2.putText(map_img, f"Lat: {lat:.6f}", (20, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(map_img, f"Lon: {lon:.6f}", (20, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(map_img, f"Alt: {self.latest_gps.altitude:.1f}m", (20, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(map_img, f"Accuracy: ±{self.latest_gps.horizontal_accuracy:.1f}m", (20, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.imshow(self.gps_window, map_img)
                self.gps_map_cache = map_img
        except Exception as e:
            print(f"❌ Error fetching GPS map: {e}")
            # Show cached map if available
            if self.gps_map_cache is not None:
                cv2.imshow(self.gps_window, self.gps_map_cache)

    def _get_osm_map(self, lat, lon, zoom, width=800, height=600):
        """Fetch OpenStreetMap tiles and composite them"""
        try:
            # Calculate tile coordinates
            n = 2.0 ** zoom
            xtile = int((lon + 180.0) / 360.0 * n)
            ytile = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)

            # Fetch multiple tiles to cover the area
            tile_size = 256
            tiles_x = (width // tile_size) + 1
            tiles_y = (height // tile_size) + 1

            # Create composite image
            composite = np.zeros((tiles_y * tile_size, tiles_x * tile_size, 3), dtype=np.uint8)

            for dy in range(tiles_y):
                for dx in range(tiles_x):
                    tile_x = xtile + dx - tiles_x // 2
                    tile_y = ytile + dy - tiles_y // 2

                    # OpenStreetMap tile URL
                    url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"

                    # Download tile
                    response = requests.get(url, headers={'User-Agent': 'ArvosSDK/1.0'}, timeout=5)
                    if response.status_code == 200:
                        tile_img = Image.open(BytesIO(response.content))
                        tile_array = np.array(tile_img)

                        # Convert RGBA to BGR if needed
                        if tile_array.shape[2] == 4:
                            tile_array = cv2.cvtColor(tile_array, cv2.COLOR_RGBA2BGR)
                        elif tile_array.shape[2] == 3:
                            tile_array = cv2.cvtColor(tile_array, cv2.COLOR_RGB2BGR)

                        # Place tile in composite
                        y_start = dy * tile_size
                        x_start = dx * tile_size
                        composite[y_start:y_start+tile_size, x_start:x_start+tile_size] = tile_array

            # Crop to desired size (centered)
            crop_y = (composite.shape[0] - height) // 2
            crop_x = (composite.shape[1] - width) // 2
            return composite[crop_y:crop_y+height, crop_x:crop_x+width]

        except Exception as e:
            print(f"Error fetching OSM tiles: {e}")
            return None

    def draw_overlay(self, frame):
        """Draw sensor data overlay on frame"""
        if frame is None:
            return None

        # Make a copy to avoid modifying original
        frame = frame.copy()

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
        """Display all windows (camera, depth, GPS)"""
        # Show camera feed
        if self.latest_frame is not None:
            display_frame = self.draw_overlay(self.latest_frame)
            if display_frame is not None:
                cv2.imshow(self.camera_window, display_frame)
        else:
            # Show placeholder if no frame yet
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for camera frames...", (100, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(self.camera_window, placeholder)

        # Show depth visualization window
        self.show_depth_window()

        # Show GPS map window
        self.show_gps_window()

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
