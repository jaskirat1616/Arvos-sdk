#!/usr/bin/env python3
"""
Debug version of MCAP HTTP server with verbose logging
"""

import asyncio
from arvos.servers import MCAPHTTPServer
from arvos.data_types import IMUData, GPSData, PoseData


async def main():
    server = MCAPHTTPServer(host="0.0.0.0", port=17500)

    # Track requests
    request_count = 0

    def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration} gyro={data.angular_velocity}")

    def on_gps(data: GPSData):
        print(f"📍 GPS: lat={data.latitude:.6f}, lon={data.longitude:.6f}, accuracy ±{data.horizontal_accuracy:.1f}m")

    def on_pose(data: PoseData):
        print(f"🧭 Pose: position={data.position} tracking={data.tracking_state}")

    def on_camera(data):
        nonlocal request_count
        request_count += 1
        if hasattr(data, 'data'):
            print(f"📸 Camera frame #{request_count}: {len(data.data)} bytes, {data.width}x{data.height}")
        else:
            print(f"📸 Camera frame #{request_count}: received")

    def on_depth(data):
        nonlocal request_count
        request_count += 1
        if hasattr(data, 'point_cloud') and hasattr(data.point_cloud, 'points'):
            print(f"🎯 Depth frame #{request_count}: {len(data.point_cloud.points)} points")
        else:
            print(f"🎯 Depth frame #{request_count}: received")

    # Monkey-patch the telemetry handler to add logging
    original_handle_telemetry = server.handle_telemetry

    async def debug_handle_telemetry(request):
        nonlocal request_count
        request_count += 1
        print(f"🔔 Request #{request_count}: POST /api/mcap/telemetry")
        try:
            result = await original_handle_telemetry(request)
            print(f"   ✅ Processed successfully")
            return result
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise

    server.handle_telemetry = debug_handle_telemetry

    # Monkey-patch the binary handler to add logging
    original_handle_binary = server.handle_binary

    async def debug_handle_binary(request):
        nonlocal request_count
        request_count += 1
        content_length = request.headers.get('Content-Length', 'unknown')
        print(f"🔔 Request #{request_count}: POST /api/mcap/binary ({content_length} bytes)")
        try:
            result = await original_handle_binary(request)
            print(f"   ✅ Processed successfully")
            return result
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise

    server.handle_binary = debug_handle_binary

    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_camera = on_camera
    server.on_depth = on_depth

    # IMPORTANT: Reconfigure parser callbacks after setting them
    server._configure_parser_callbacks()

    print("🔍 DEBUG MODE: Waiting for MCAP HTTP POST data...")
    print("   All requests will be logged with details")
    print("   Press Ctrl+C to stop.")
    print()

    try:
        await server.start()
    except KeyboardInterrupt:
        print(f"\n📊 Total requests received: {request_count}")
        print("\nStopping server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
