#!/usr/bin/env python3
"""
GPS Viewer - Dedicated GPS display process

Connects to Arvos server and displays ONLY GPS data.
Part of modular ROS-like architecture.

Usage:
    python gps_viewer.py [--port 9090]
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, GPSData
import argparse
import math
import requests
from io import BytesIO
from PIL import Image


class GPSViewer:
    def __init__(self):
        self.latest_gps = None
        self.map_cache = None
        self.last_pos = None

    def update_gps(self, data: GPSData):
        """Store GPS data"""
        self.latest_gps = data
        print(f"🌍 GPS: ({data.latitude:.6f}, {data.longitude:.6f}), ±{data.horizontal_accuracy:.1f}m")

    def render(self):
        """Render GPS map"""
        if self.latest_gps is None:
            placeholder = np.zeros((600, 800, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for GPS...", (250, 300),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('GPS', placeholder)
            return

        lat, lon = self.latest_gps.latitude, self.latest_gps.longitude

        # Check if moved significantly
        if self.last_pos is not None:
            lat_diff = abs(lat - self.last_pos[0])
            lon_diff = abs(lon - self.last_pos[1])
            if lat_diff < 0.0001 and lon_diff < 0.0001:
                # Use cache
                if self.map_cache is not None:
                    cv2.imshow('GPS', self.map_cache)
                return

        # Fetch new map
        try:
            map_img = self._fetch_map(lat, lon, zoom=17)

            if map_img is not None:
                # Add marker
                center_x, center_y = 400, 300
                cv2.circle(map_img, (center_x, center_y), 10, (0, 0, 255), -1)
                cv2.circle(map_img, (center_x, center_y), 12, (255, 255, 255), 2)

                # Info overlay
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
                self.map_cache = map_img
                self.last_pos = (lat, lon)

        except Exception as e:
            print(f"❌ GPS error: {e}")
            if self.map_cache is not None:
                cv2.imshow('GPS', self.map_cache)

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

            crop_y = (composite.shape[0] - height) // 2
            crop_x = (composite.shape[1] - width) // 2
            return composite[crop_y:crop_y+height, crop_x:crop_x+width]

        except:
            return None


async def main():
    parser = argparse.ArgumentParser(description='Arvos GPS Viewer')
    parser.add_argument('--port', type=int, default=9090, help='Server port')
    args = parser.parse_args()

    print(f"🌍 GPS Viewer")
    print(f"📡 Connecting to port {args.port}...")

    viewer = GPSViewer()
    server = ArvosServer(port=args.port)

    # Only GPS callback
    server.on_gps = viewer.update_gps

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
    print("👋 GPS viewer closed")


if __name__ == "__main__":
    asyncio.run(main())
