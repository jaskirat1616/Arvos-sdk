#!/usr/bin/env python3
"""
Arvos Live View - Optimized for Performance

Shows camera, depth map, and GPS with stable 15-25 FPS.

Usage:
    python simple_camera_view.py
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, CameraFrame, DepthFrame, GPSData, IMUData, PoseData
import time
import math
import requests
from io import BytesIO
from PIL import Image


class SimpleCameraView:
    def __init__(self):
        # Camera
        self.latest_frame = None
        self.frame_count = 0
        self.total_frames = 0
        self.fps = 0.0
        self.last_fps_time = time.time()

        # Depth
        self.latest_depth = None
        self.depth_frame_count = 0

        # GPS
        self.latest_gps = None
        self.gps_map_cache = None
        self.last_gps_pos = None

    def update_camera(self, frame: CameraFrame):
        """Decode and store frame"""
        try:
            # Fast OpenCV decode
            img = cv2.imdecode(np.frombuffer(frame.data, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.latest_frame = img
            self.total_frames += 1

            # Calculate FPS
            self.frame_count += 1
            now = time.time()
            elapsed = now - self.last_fps_time
            if elapsed >= 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.last_fps_time = now
                print(f"📷 FPS: {self.fps:.1f}")

        except Exception as e:
            print(f"❌ Decode error: {e}")

    def update_depth(self, frame: DepthFrame):
        """Store depth data"""
        self.latest_depth = frame
        self.depth_frame_count += 1
        if self.depth_frame_count % 10 == 0:
            print(f"🔵 Depth: {frame.point_count} points")

    def update_gps(self, data: GPSData):
        """Store GPS data"""
        self.latest_gps = data
        print(f"🌍 GPS: ({data.latitude:.6f}, {data.longitude:.6f})")

    def update_imu(self, data: IMUData):
        """Store IMU (not displayed to save FPS)"""
        pass

    def update_pose(self, data: PoseData):
        """Store pose (not displayed to save FPS)"""
        pass


    def show_camera(self):
        """Show camera with minimal overlay"""
        if self.latest_frame is not None:
            # Copy for safety
            frame = self.latest_frame.copy()

            # Minimal FPS overlay only
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

            cv2.imshow('Camera', frame)
        else:
            # Placeholder
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting...", (200, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Camera', placeholder)

    def show_depth(self):
        """Show fast 2D depth map"""
        if self.latest_depth is None or self.latest_depth.point_count == 0:
            # Placeholder
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "No depth data", (180, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Depth', placeholder)
            return

        try:
            # Parse point cloud
            points = self.latest_depth.to_point_cloud()
            if points is None or len(points) == 0:
                return

            # Get XYZ
            xyz = points[:, :3] if points.shape[1] >= 3 else None
            if xyz is None:
                return

            # Filter NaN/inf
            valid = np.all(np.isfinite(xyz), axis=1)
            xyz = xyz[valid]
            if len(xyz) == 0:
                return

            # Fast vectorized 2D projection
            x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]

            # Create depth map
            W, H = 640, 480
            depth_img = np.zeros((H, W), dtype=np.float32)
            count_img = np.zeros((H, W), dtype=np.int32)

            # Project to image coords (clip to avoid overflow)
            img_x = np.clip(((x + 2.0) / 4.0 * W).astype(int), 0, W-1)
            img_y = np.clip(((z + 2.0) / 4.0 * H).astype(int), 0, H-1)
            depths = np.abs(y)

            # Accumulate
            np.add.at(depth_img, (img_y, img_x), depths)
            np.add.at(count_img, (img_y, img_x), 1)

            # Average
            mask = count_img > 0
            depth_img[mask] /= count_img[mask]

            # Normalize and colorize
            if depth_img.max() > 0:
                depth_norm = np.clip(depth_img / depth_img.max(), 0, 1)
            else:
                depth_norm = depth_img

            # Apply colormap
            depth_colored = cv2.applyColorMap((depth_norm * 255).astype(np.uint8), cv2.COLORMAP_JET)
            depth_colored[~mask] = [0, 0, 0]

            # Add info
            cv2.putText(depth_colored, f"Points: {len(xyz)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow('Depth', depth_colored)

        except Exception as e:
            print(f"❌ Depth error: {e}")

    def show_gps(self):
        """Show GPS map with caching"""
        if self.latest_gps is None:
            # Placeholder
            placeholder = np.zeros((600, 800, 3), dtype=np.uint8)
            cv2.putText(placeholder, "No GPS data", (280, 300),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('GPS', placeholder)
            return

        # Check if GPS moved significantly
        lat, lon = self.latest_gps.latitude, self.latest_gps.longitude
        if self.last_gps_pos is not None:
            lat_diff = abs(lat - self.last_gps_pos[0])
            lon_diff = abs(lon - self.last_gps_pos[1])
            # ~0.0001 degrees = ~11 meters
            if lat_diff < 0.0001 and lon_diff < 0.0001:
                # Use cached map
                if self.gps_map_cache is not None:
                    cv2.imshow('GPS', self.gps_map_cache)
                return

        # Fetch new map
        try:
            zoom = 17
            map_img = self._fetch_map(lat, lon, zoom)

            if map_img is not None:
                # Add marker
                center_x, center_y = 400, 300
                cv2.circle(map_img, (center_x, center_y), 10, (0, 0, 255), -1)
                cv2.circle(map_img, (center_x, center_y), 12, (255, 255, 255), 2)

                # Add overlay
                overlay = map_img.copy()
                cv2.rectangle(overlay, (10, 10), (350, 100), (0, 0, 0), -1)
                map_img = cv2.addWeighted(overlay, 0.6, map_img, 0.4, 0)

                cv2.putText(map_img, f"Lat: {lat:.6f}", (20, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(map_img, f"Lon: {lon:.6f}", (20, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(map_img, f"Acc: ±{self.latest_gps.horizontal_accuracy:.1f}m", (20, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.imshow('GPS', map_img)
                self.gps_map_cache = map_img
                self.last_gps_pos = (lat, lon)

        except Exception as e:
            print(f"❌ GPS error: {e}")
            # Show cached if available
            if self.gps_map_cache is not None:
                cv2.imshow('GPS', self.gps_map_cache)

    def _fetch_map(self, lat, lon, zoom, width=800, height=600):
        """Fetch OpenStreetMap tiles"""
        try:
            n = 2.0 ** zoom
            xtile = int((lon + 180.0) / 360.0 * n)
            ytile = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)

            tile_size = 256
            tiles_x = (width // tile_size) + 1
            tiles_y = (height // tile_size) + 1

            composite = np.zeros((tiles_y * tile_size, tiles_x * tile_size, 3), dtype=np.uint8)

            for dy in range(tiles_y):
                for dx in range(tiles_x):
                    tile_x = xtile + dx - tiles_x // 2
                    tile_y = ytile + dy - tiles_y // 2

                    url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"
                    response = requests.get(url, headers={'User-Agent': 'ArvosSDK/1.0'}, timeout=3)

                    if response.status_code == 200:
                        tile_img = Image.open(BytesIO(response.content))
                        tile_array = np.array(tile_img)

                        if len(tile_array.shape) == 3:
                            if tile_array.shape[2] == 4:
                                tile_array = cv2.cvtColor(tile_array, cv2.COLOR_RGBA2BGR)
                            else:
                                tile_array = cv2.cvtColor(tile_array, cv2.COLOR_RGB2BGR)

                        y_start = dy * tile_size
                        x_start = dx * tile_size
                        composite[y_start:y_start+tile_size, x_start:x_start+tile_size] = tile_array

            # Crop to size
            crop_y = (composite.shape[0] - height) // 2
            crop_x = (composite.shape[1] - width) // 2
            return composite[crop_y:crop_y+height, crop_x:crop_x+width]

        except:
            return None


async def main():
    print("🚀 Arvos Live View - Optimized")
    print("📱 Connect iPhone")
    print("Press 'q' to quit\n")

    viewer = SimpleCameraView()
    server = ArvosServer(port=9090)

    # Set callbacks
    server.on_camera = viewer.update_camera
    server.on_depth = viewer.update_depth
    server.on_gps = viewer.update_gps
    server.on_imu = viewer.update_imu
    server.on_pose = viewer.update_pose

    async def on_connect(client_id: str):
        print(f"✅ Connected: {client_id}\n")

    server.on_connect = on_connect

    # Start server
    server_task = asyncio.create_task(server.start())

    # Display loop
    running = True
    frame_count = 0

    # Show placeholder windows immediately
    print("Opening windows...")
    viewer.show_camera()
    viewer.show_depth()
    viewer.show_gps()

    while running:
        frame_count += 1

        # Camera: every frame
        viewer.show_camera()

        # Depth: every 20 frames (~1 per second at 20 FPS)
        if frame_count % 20 == 0:
            viewer.show_depth()

        # GPS: every 60 frames (~once every 3 seconds)
        if frame_count % 60 == 0:
            viewer.show_gps()

        # Process events
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            running = False
            break

        # Yield to async
        await asyncio.sleep(0)

    cv2.destroyAllWindows()
    print("\n👋 Done")


if __name__ == "__main__":
    asyncio.run(main())
