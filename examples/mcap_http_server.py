#!/usr/bin/env python3
"""
Example MCAP HTTP server for receiving sensor data from the ARVOS iOS app.

This server receives sensor data via HTTP POST endpoints (compatible with the iOS MCAP adapter)
and writes it to an MCAP file, which can be viewed in Foxglove Studio.

Run this script, then in the iOS app select the MCAP Stream protocol and point it at
the printed connection URL.

Requirements:
    pip install mcap aiohttp
"""

import asyncio
from arvos.servers import MCAPHTTPServer
from arvos.data_types import IMUData, GPSData, PoseData


async def main():
    server = MCAPHTTPServer(host="0.0.0.0", port=17500)

    def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration} gyro={data.angular_velocity}")

    def on_gps(data: GPSData):
        print(f"📍 GPS: lat={data.latitude:.6f}, lon={data.longitude:.6f}, accuracy ±{data.horizontal_accuracy:.1f}m")

    def on_pose(data: PoseData):
        print(f"🧭 Pose: position={data.position} tracking={data.tracking_state}")

    def on_camera(data):
        if hasattr(data, 'data'):
            print(f"📸 Camera frame: {len(data.data)} bytes, {data.width}x{data.height}")
        else:
            print(f"📸 Camera frame received")

    def on_depth(data):
        if hasattr(data, 'point_cloud') and hasattr(data.point_cloud, 'points'):
            print(f"🎯 Depth frame: {len(data.point_cloud.points)} points")
        else:
            print(f"🎯 Depth frame received")

    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_camera = on_camera
    server.on_depth = on_depth

    # IMPORTANT: Reconfigure parser callbacks after setting them
    server._configure_parser_callbacks()

    print("Waiting for MCAP HTTP POST data... Press Ctrl+C to stop.")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
