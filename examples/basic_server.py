#!/usr/bin/env python3
"""
Basic Arvos Server Example

This example shows how to set up a simple server that receives
all sensor data from the Arvos iPhone app.

Usage:
    python basic_server.py

Then scan the QR code with your iPhone running Arvos.
"""

import asyncio
from arvos import ArvosServer, IMUData, GPSData, PoseData, CameraFrame, DepthFrame, HandshakeMessage


async def main():
    # Create server
    server = ArvosServer(port=9090)

    # Track statistics
    stats = {
        "imu_count": 0,
        "gps_count": 0,
        "pose_count": 0,
        "camera_count": 0,
        "depth_count": 0
    }

    # Handle handshake
    async def on_handshake(handshake: HandshakeMessage):
        print(f"\n🤝 Handshake received:")
        print(f"   Device: {handshake.device_name}")
        print(f"   Model: {handshake.device_model}")
        print(f"   iOS: {handshake.os_version}")
        print(f"   App Version: {handshake.app_version}")
        print(f"   Has LiDAR: {handshake.capabilities.has_lidar}")
        print(f"   Has ARKit: {handshake.capabilities.has_arkit}")
        print(f"   Has GPS: {handshake.capabilities.has_gps}")
        print(f"   Supported Modes: {', '.join(handshake.capabilities.supported_modes)}")
        print()

    # Handle IMU data
    async def on_imu(data: IMUData):
        stats["imu_count"] += 1
        if stats["imu_count"] % 100 == 0:  # Print every 100th sample
            print(f"📊 IMU [{stats['imu_count']}]: "
                  f"accel=({data.linear_acceleration[0]:.2f}, {data.linear_acceleration[1]:.2f}, {data.linear_acceleration[2]:.2f}) m/s², "
                  f"gyro=({data.angular_velocity[0]:.2f}, {data.angular_velocity[1]:.2f}, {data.angular_velocity[2]:.2f}) rad/s")

    # Handle GPS data
    async def on_gps(data: GPSData):
        stats["gps_count"] += 1
        print(f"🌍 GPS [{stats['gps_count']}]: "
              f"lat={data.latitude:.6f}, lon={data.longitude:.6f}, "
              f"alt={data.altitude:.1f}m, accuracy={data.horizontal_accuracy:.1f}m")

    # Handle pose data
    async def on_pose(data: PoseData):
        stats["pose_count"] += 1
        if stats["pose_count"] % 30 == 0:  # Print every 30th sample (1 per second at 30 Hz)
            print(f"📍 Pose [{stats['pose_count']}]: "
                  f"pos=({data.position[0]:.3f}, {data.position[1]:.3f}, {data.position[2]:.3f})m, "
                  f"tracking={data.tracking_state}")

    # Handle camera frames
    async def on_camera(frame: CameraFrame):
        stats["camera_count"] += 1
        print(f"📷 Camera [{stats['camera_count']}]: "
              f"{frame.width}x{frame.height}, "
              f"{frame.size_kb:.1f} KB, "
              f"format={frame.format}")

    # Handle depth frames
    async def on_depth(frame: DepthFrame):
        stats["depth_count"] += 1
        print(f"🔷 Depth [{stats['depth_count']}]: "
              f"{frame.point_count} points, "
              f"range={frame.min_depth:.2f}-{frame.max_depth:.2f}m, "
              f"{frame.size_kb:.1f} KB")

    # Handle connection/disconnection
    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}\n")

    async def on_disconnect(client_id: str):
        print(f"\n❌ Client disconnected: {client_id}")
        print(f"\nSession Statistics:")
        print(f"  IMU samples: {stats['imu_count']}")
        print(f"  GPS samples: {stats['gps_count']}")
        print(f"  Pose samples: {stats['pose_count']}")
        print(f"  Camera frames: {stats['camera_count']}")
        print(f"  Depth frames: {stats['depth_count']}")

    # Assign handlers
    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_handshake = on_handshake
    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_camera = on_camera
    server.on_depth = on_depth

    # Start server
    print("🚀 Starting Arvos server...")
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
