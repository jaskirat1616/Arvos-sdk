#!/usr/bin/env python3
"""
Simple Apple Watch Sensor Receiver

Minimal example showing how to receive Apple Watch sensor data from iPhone.

Usage:
    python examples/simple_watch_receiver.py
"""

import asyncio
from arvos import ArvosServer
from arvos.data_types import WatchIMUData, WatchAttitudeData, WatchMotionActivityData
import math


async def main():
    """Simple example receiving Apple Watch sensor data"""

    # Create server
    server = ArvosServer(port=9090)

    # Show QR code for connection
    server.print_qr_code()

    # Define callbacks
    async def on_watch_imu(data: WatchIMUData):
        """Handle Watch IMU data"""
        accel = data.linear_acceleration
        gyro = data.angular_velocity

        print(f"Watch IMU: accel=({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f}) m/s², "
              f"gyro=({gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f}) rad/s")

    async def on_watch_attitude(data: WatchAttitudeData):
        """Handle Watch attitude data"""
        pitch_deg = math.degrees(data.pitch)
        roll_deg = math.degrees(data.roll)
        yaw_deg = math.degrees(data.yaw)

        print(f"Watch Attitude: pitch={pitch_deg:.1f}°, roll={roll_deg:.1f}°, yaw={yaw_deg:.1f}°")

    async def on_watch_activity(data: WatchMotionActivityData):
        """Handle Watch motion activity"""
        print(f"🏃 Motion Activity: {data.state.upper()} (confidence: {data.confidence:.1%})")

    # Assign callbacks
    server.on_watch_imu = on_watch_imu
    server.on_watch_attitude = on_watch_attitude
    server.on_watch_activity = on_watch_activity

    print("\n📱 Instructions:")
    print("  1. Open Arvos app on iPhone")
    print("  2. Make sure Apple Watch is paired and companion app installed")
    print("  3. Enable 'Apple Watch' in Arvos app settings")
    print("  4. Scan QR code and start streaming")
    print("\nWaiting for data...\n")

    # Start server
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
