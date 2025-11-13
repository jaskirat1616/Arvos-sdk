#!/usr/bin/env python3
"""
Example gRPC server for receiving sensor data from the ARVOS iOS app.

Run this script, then in the iOS app select the gRPC protocol and point it at
the printed connection URL (or manually enter the host and port).

Note: gRPC requires iOS 18+ on the iPhone.
"""

import asyncio
from arvos.servers import GRPCArvosServer
from arvos.data_types import IMUData, GPSData, PoseData


async def main():
    server = GRPCArvosServer(host="0.0.0.0", port=50051)

    async def on_connect(client_id: str):
        print(f"✅ gRPC client connected: {client_id}")

    async def on_disconnect(client_id: str):
        print(f"👋 gRPC client disconnected: {client_id}")

    def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration} gyro={data.angular_velocity}")

    def on_gps(data: GPSData):
        print(f"📍 GPS: lat={data.latitude:.6f}, lon={data.longitude:.6f}, accuracy ±{data.horizontal_accuracy:.1f}m")

    def on_pose(data: PoseData):
        print(f"🧭 Pose: position={data.position} tracking={data.tracking_state}")

    def on_handshake(handshake):
        print(f"🤝 Handshake: {handshake.device_name} ({handshake.device_model})")
        print(f"   OS: {handshake.os_version}, App: {handshake.app_version}")
        if handshake.capabilities:
            caps = handshake.capabilities
            print(f"   Capabilities: LiDAR={caps.has_lidar}, ARKit={caps.has_arkit}, GPS={caps.has_gps}")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_handshake = on_handshake

    server.print_connection_info()
    print("Waiting for gRPC sensor data... Press Ctrl+C to stop.")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())

