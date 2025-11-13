#!/usr/bin/env python3
"""
Example HTTP server for receiving sensor data from the ARVOS iOS app.

Run this script, then in the iOS app select the HTTP protocol and point it at
the printed connection URL (or scan the QR code generated below).
"""

import asyncio
from arvos.servers import HTTPArvosServer
from arvos.data_types import IMUData, GPSData, PoseData


async def main():
    server = HTTPArvosServer(port=8080)

    async def on_connect(client_id: str):
        print(f"✅ HTTP client connected: {client_id}")

    async def on_disconnect(client_id: str):
        print(f"👋 HTTP client disconnected: {client_id}")

    def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration} gyro={data.angular_velocity}")

    def on_gps(data: GPSData):
        print(f"📍 GPS: lat={data.latitude:.6f}, lon={data.longitude:.6f}, accuracy ±{data.horizontal_accuracy:.1f}m")

    def on_pose(data: PoseData):
        print(f"🧭 Pose: position={data.position} tracking={data.tracking_state}")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose

    server.print_connection_info()
    print("Waiting for HTTP telemetry... Press Ctrl+C to stop.")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("Stopping server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())


