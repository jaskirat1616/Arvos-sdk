#!/usr/bin/env python3
"""
Example MCAP Stream server for receiving sensor data from the ARVOS iOS app.

This example receives sensor data and writes it to an MCAP file, which can be
viewed in Foxglove Studio or other MCAP-compatible tools.

Run this script, then in the iOS app select the MCAP Stream protocol and point it at
the printed connection URL.

Requirements:
    pip install mcap websockets
"""

import asyncio
from arvos.servers import MCAPStreamServer
from arvos.data_types import IMUData, GPSData, PoseData


async def main():
    server = MCAPStreamServer(host="0.0.0.0", port=17500)

    async def on_connect(client_id: str):
        print(f"✅ MCAP client connected: {client_id}")

    async def on_disconnect(client_id: str):
        print(f"👋 MCAP client disconnected: {client_id}")

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
    print("Waiting for MCAP stream data... Press Ctrl+C to stop.")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())

