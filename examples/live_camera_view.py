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
import concurrent.futures
import threading


class LiveCameraView:
    def __init__(self):
        self.latest_frame = None
        self.latest_imu = None
        self.latest_pose = None
        self.latest_depth = None
        self.latest_gps = None
        self.frame_count = 0
        self.total_frames = 0  # Total frames received (never reset)
        self.depth_count = 0
        self.fps = 0
        self.last_time = datetime.now()

        # GPS map cache
        self.gps_map_cache = None
        self.last_gps_update = None

        # Window names
        self.camera_window = 'Arvos - Camera Feed'
        self.gps_window = 'Arvos - GPS Map'

        # Main thread display flag (macOS requires GUI on main thread)
        self.running = False

    def update_camera(self, frame: CameraFrame):
        """Update camera frame"""
        # Decode JPEG directly with OpenCV (faster than PIL)
        try:
            # Decode JPEG from bytes using cv2 (much faster than PIL)
            img_bgr = cv2.imdecode(np.frombuffer(frame.data, dtype=np.uint8), cv2.IMREAD_COLOR)

            self.latest_frame = img_bgr
            self.frame_count += 1
            self.total_frames += 1

            # Calculate FPS
            now = datetime.now()
            elapsed = (now - self.last_time).total_seconds()
            if elapsed > 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.last_time = now

            # Print first few frames and periodic updates
            if self.total_frames <= 5 or self.total_frames % 30 == 0:
                print(f"📷 Camera frame #{self.total_frames}: {frame.width}x{frame.height}, FPS: {self.fps:.1f}")

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
        """Display fast 2D depth visualization using OpenCV"""
        if self.latest_depth is None:
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for depth data...", (180, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Arvos - Depth Map', placeholder)
            return

        # Parse point cloud
        try:
            points = self.latest_depth.to_point_cloud()
            if points is None or len(points) == 0:
                return
        except Exception as e:
            print(f"❌ Error parsing point cloud: {e}")
            return

        # Extract XYZ coordinates
        if points.shape[1] >= 3:
            xyz = points[:, :3]
        else:
            return

        # Filter out NaN and inf values
        valid_mask = np.all(np.isfinite(xyz), axis=1)
        xyz = xyz[valid_mask]

        if len(xyz) == 0:
            return

        # Create fast 2D depth map projection
        depth_width, depth_height = 640, 480
        depth_image = np.zeros((depth_height, depth_width), dtype=np.float32)
        count_image = np.zeros((depth_height, depth_width), dtype=np.int32)

        # Fast vectorized projection
        x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]

        # Map to image coordinates
        img_x = ((x + 2.0) / 4.0 * depth_width).astype(int)
        img_y = ((z + 2.0) / 4.0 * depth_height).astype(int)

        # Filter valid coordinates
        valid = (img_x >= 0) & (img_x < depth_width) & (img_y >= 0) & (img_y < depth_height)
        img_x = img_x[valid]
        img_y = img_y[valid]
        depths = np.abs(y[valid])

        # Accumulate depths
        np.add.at(depth_image, (img_y, img_x), depths)
        np.add.at(count_image, (img_y, img_x), 1)

        # Average where multiple points
        mask = count_image > 0
        depth_image[mask] /= count_image[mask]

        # Normalize and colorize
        if depth_image.max() > 0:
            depth_normalized = depth_image / depth_image.max()
        else:
            depth_normalized = depth_image

        # Apply colormap (JET: blue=close, red=far)
        depth_colored = cv2.applyColorMap((depth_normalized * 255).astype(np.uint8), cv2.COLORMAP_JET)
        depth_colored[~mask] = [0, 0, 0]  # Black background

        # Add stats overlay
        cv2.putText(depth_colored, f"Points: {len(xyz):,}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(depth_colored, f"Range: {self.latest_depth.min_depth:.2f}-{self.latest_depth.max_depth:.2f}m",
                   (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('Arvos - Depth Map', depth_colored)

    def _depth_to_color(self, depths):
        """Convert depth values to colors (blue = close, red = far)"""
        if len(depths) == 0:
            return np.zeros((0, 3), dtype=np.uint8)

        # Normalize depths to 0-1
        min_d = np.nanmin(depths) if not np.all(np.isnan(depths)) else -1.0
        max_d = np.nanmax(depths) if not np.all(np.isnan(depths)) else 1.0

        if max_d == min_d:
            max_d = min_d + 1.0

        normalized = np.clip((depths - min_d) / (max_d - min_d), 0, 1)
        normalized = np.nan_to_num(normalized, 0.5)  # Replace NaN with 0.5

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

        # Only update map if GPS changed significantly (more than 10 meters)
        if self.last_gps_update is not None:
            lat_diff = abs(self.latest_gps.latitude - self.last_gps_update[0])
            lon_diff = abs(self.latest_gps.longitude - self.last_gps_update[1])
            # ~0.0001 degrees = ~11 meters
            if lat_diff < 0.0001 and lon_diff < 0.0001:
                # Use cached map
                if self.gps_map_cache is not None:
                    cv2.imshow(self.gps_window, self.gps_map_cache)
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
                self.last_gps_update = (lat, lon)
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
                        if len(tile_array.shape) == 3 and tile_array.shape[2] == 4:
                            tile_array = cv2.cvtColor(tile_array, cv2.COLOR_RGBA2BGR)
                        elif len(tile_array.shape) == 3 and tile_array.shape[2] == 3:
                            tile_array = cv2.cvtColor(tile_array, cv2.COLOR_RGB2BGR)
                        elif len(tile_array.shape) == 2:
                            # Grayscale image, convert to BGR
                            tile_array = cv2.cvtColor(tile_array, cv2.COLOR_GRAY2BGR)

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
        """Draw minimal overlay - FAST version"""
        if frame is None:
            return None

        # Don't copy - draw directly (faster)
        # Just show FPS in corner
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        return frame

    def show(self):
        """Display all windows - MUST run on main thread for macOS"""
        # Show camera feed ONLY (fastest possible)
        if self.latest_frame is not None:
            # Add FPS overlay
            cv2.putText(self.latest_frame, f"FPS: {self.fps:.1f}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(self.camera_window, self.latest_frame)
        else:
            # Show placeholder if no frame yet
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for camera...", (150, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(self.camera_window, placeholder)

        # Disable depth and GPS temporarily to test max FPS
        # if self.total_frames % 30 == 0 and self.total_frames > 0:
        #     self.show_depth_window()
        # if self.total_frames % 60 == 0 and self.total_frames > 0:
        #     self.show_gps_window()

        # Process events (MUST call for windows to update)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False

        return True


async def main():
    """Main function with async server and sync display"""
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

    print("📡 Starting server...")

    # Start server task
    server_task = asyncio.create_task(server.start())

    viewer.running = True

    # Display loop as async task
    async def display_loop():
        while viewer.running:
            if not viewer.show():
                viewer.running = False
                break
            await asyncio.sleep(0)  # Yield to other tasks immediately

    try:
        # Run server and display concurrently
        await asyncio.gather(
            server_task,
            display_loop(),
            return_exceptions=True
        )
    except KeyboardInterrupt:
        pass
    finally:
        viewer.running = False
        cv2.destroyAllWindows()
        print("\n👋 Camera view closed")


if __name__ == "__main__":
    asyncio.run(main())
