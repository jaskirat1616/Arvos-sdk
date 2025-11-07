#!/usr/bin/env python3
"""
Debug server - prints all received sensor data

Simple test to verify data is being received from iPhone.
"""

import asyncio
from arvos import ArvosServer, IMUData, PoseData, CameraFrame, DepthFrame, GPSData


async def main():
    print("🔍 Starting Arvos Debug Server")
    print("📱 Connect your iPhone running Arvos\n")

    # Create server
    server = ArvosServer(port=9090)

    # Stats
    camera_count = 0
    depth_count = 0
    gps_count = 0
    imu_count = 0
    pose_count = 0

    # Callbacks with counters
    def on_camera(frame: CameraFrame):
        nonlocal camera_count
        camera_count += 1
        print(f"📷 Camera frame {camera_count}: {frame.width}x{frame.height}, {len(frame.data)} bytes")

    def on_depth(frame: DepthFrame):
        nonlocal depth_count
        depth_count += 1
        print(f"🔵 Depth frame {depth_count}: {frame.point_count} points, range {frame.min_depth:.2f}-{frame.max_depth:.2f}m")

    def on_gps(data: GPSData):
        nonlocal gps_count
        gps_count += 1
        print(f"🌍 GPS update {gps_count}: ({data.latitude:.6f}, {data.longitude:.6f}), accuracy ±{data.horizontal_accuracy:.1f}m")

    def on_imu(data: IMUData):
        nonlocal imu_count
        imu_count += 1
        if imu_count % 10 == 0:  # Only print every 10th IMU update
            print(f"📊 IMU update {imu_count}: accel={data.linear_acceleration}, gyro={data.angular_velocity}")

    def on_pose(data: PoseData):
        nonlocal pose_count
        pose_count += 1
        if pose_count % 5 == 0:  # Only print every 5th pose update
            print(f"🎯 Pose update {pose_count}: pos={data.position}, tracking={data.tracking_state}")

    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}\n")

    async def on_disconnect(client_id: str):
        print(f"\n❌ Client disconnected: {client_id}")
        print(f"\n📊 Final Stats:")
        print(f"   Camera frames: {camera_count}")
        print(f"   Depth frames: {depth_count}")
        print(f"   GPS updates: {gps_count}")
        print(f"   IMU updates: {imu_count}")
        print(f"   Pose updates: {pose_count}")

    # Set up callbacks
    server.on_camera = on_camera
    server.on_depth = on_depth
    server.on_gps = on_gps
    server.on_imu = on_imu
    server.on_pose = on_pose
    server.on_connect = on_connect
    server.on_disconnect = on_disconnect

    # Start server
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        print(f"\n📊 Final Stats:")
        print(f"   Camera frames: {camera_count}")
        print(f"   Depth frames: {depth_count}")
        print(f"   GPS updates: {gps_count}")
        print(f"   IMU updates: {imu_count}")
        print(f"   Pose updates: {pose_count}")


if __name__ == "__main__":
    asyncio.run(main())
