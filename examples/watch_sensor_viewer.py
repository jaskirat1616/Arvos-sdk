#!/usr/bin/env python3
"""
Apple Watch Sensor Viewer

This example demonstrates receiving and displaying sensor data from Apple Watch
connected to the iPhone running Arvos app.

Features:
- Real-time IMU data (accelerometer + gyroscope + gravity) at 50-100 Hz
- Attitude/pose data (quaternion + Euler angles)
- Motion activity classification (walking, running, cycling, vehicle, stationary)
- Live statistics and visualization

Requirements:
- Apple Watch paired with iPhone running Arvos
- Watch sensors enabled in Arvos app settings
- Both devices on same network as this computer

Usage:
    python examples/watch_sensor_viewer.py
"""

import asyncio
from arvos import ArvosServer
from arvos.data_types import WatchIMUData, WatchAttitudeData, WatchMotionActivityData
import time
from collections import deque
import math


class WatchSensorViewer:
    """Viewer for Apple Watch sensor data with live statistics"""

    def __init__(self):
        self.server = ArvosServer(port=9090)

        # Statistics
        self.imu_count = 0
        self.attitude_count = 0
        self.activity_count = 0
        self.start_time = None

        # Latest data
        self.latest_imu = None
        self.latest_attitude = None
        self.latest_activity = None

        # Rate tracking (last 100 samples)
        self.imu_timestamps = deque(maxlen=100)

        # Setup callbacks
        self.server.on_watch_imu = self.on_watch_imu
        self.server.on_watch_attitude = self.on_watch_attitude
        self.server.on_watch_activity = self.on_watch_activity
        self.server.on_connect = self.on_connect

    async def on_connect(self, client_id: str):
        """Handle client connection"""
        print(f"\n✅ Device connected: {client_id}")
        print("Waiting for Apple Watch sensor data...")
        print("(Make sure Watch sensors are enabled in Arvos app)\n")

    async def on_watch_imu(self, data: WatchIMUData):
        """Handle Watch IMU data"""
        if self.start_time is None:
            self.start_time = time.time()

        self.imu_count += 1
        self.latest_imu = data
        self.imu_timestamps.append(data.timestamp_s)

        # Print every 10th sample to avoid spam
        if self.imu_count % 10 == 0:
            self.print_status()

    async def on_watch_attitude(self, data: WatchAttitudeData):
        """Handle Watch attitude/pose data"""
        self.attitude_count += 1
        self.latest_attitude = data

    async def on_watch_activity(self, data: WatchMotionActivityData):
        """Handle Watch motion activity classification"""
        self.activity_count += 1
        self.latest_activity = data

        # Print activity changes
        print(f"\n🏃 Motion Activity: {data.state.upper()} (confidence: {data.confidence:.1%})")

    def print_status(self):
        """Print current status and latest data"""
        # Clear screen (works on Unix-like systems)
        print("\033[2J\033[H", end="")

        print("=" * 70)
        print("        APPLE WATCH SENSOR VIEWER")
        print("=" * 70)

        # Connection status
        uptime = time.time() - self.start_time if self.start_time else 0
        print(f"\n📊 Session Stats:")
        print(f"  Uptime: {uptime:.1f}s")
        print(f"  IMU samples: {self.imu_count}")
        print(f"  Attitude samples: {self.attitude_count}")
        print(f"  Activity updates: {self.activity_count}")

        # Calculate rate
        if len(self.imu_timestamps) >= 2:
            time_span = self.imu_timestamps[-1] - self.imu_timestamps[0]
            if time_span > 0:
                rate = (len(self.imu_timestamps) - 1) / time_span
                print(f"  IMU rate: {rate:.1f} Hz")

        # Latest IMU data
        if self.latest_imu:
            print(f"\n⌚ Watch IMU Data:")
            accel = self.latest_imu.linear_acceleration
            gyro = self.latest_imu.angular_velocity
            grav = self.latest_imu.gravity

            # Calculate magnitudes
            accel_mag = math.sqrt(accel[0]**2 + accel[1]**2 + accel[2]**2)
            gyro_mag = math.sqrt(gyro[0]**2 + gyro[1]**2 + gyro[2]**2)

            print(f"  Acceleration: [{accel[0]:7.3f}, {accel[1]:7.3f}, {accel[2]:7.3f}] m/s² (mag: {accel_mag:.3f})")
            print(f"  Gyroscope:    [{gyro[0]:7.3f}, {gyro[1]:7.3f}, {gyro[2]:7.3f}] rad/s (mag: {gyro_mag:.3f})")
            print(f"  Gravity:      [{grav[0]:7.3f}, {grav[1]:7.3f}, {grav[2]:7.3f}] m/s²")

            # Visual bars for acceleration
            print(f"\n  Accel X: {self.make_bar(accel[0], -20, 20)}")
            print(f"  Accel Y: {self.make_bar(accel[1], -20, 20)}")
            print(f"  Accel Z: {self.make_bar(accel[2], -20, 20)}")

        # Latest attitude data
        if self.latest_attitude:
            print(f"\n🧭 Watch Attitude:")
            pitch_deg = math.degrees(self.latest_attitude.pitch)
            roll_deg = math.degrees(self.latest_attitude.roll)
            yaw_deg = math.degrees(self.latest_attitude.yaw)

            print(f"  Pitch: {pitch_deg:7.2f}°  {self.make_bar(pitch_deg, -180, 180, width=30)}")
            print(f"  Roll:  {roll_deg:7.2f}°  {self.make_bar(roll_deg, -180, 180, width=30)}")
            print(f"  Yaw:   {yaw_deg:7.2f}°  {self.make_bar(yaw_deg, -180, 180, width=30)}")

            quat = self.latest_attitude.quaternion
            print(f"  Quaternion: [{quat[0]:.3f}, {quat[1]:.3f}, {quat[2]:.3f}, {quat[3]:.3f}]")
            print(f"  Frame: {self.latest_attitude.reference_frame}")

        # Latest activity data
        if self.latest_activity:
            print(f"\n🏃 Motion Activity: {self.latest_activity.state.upper()}")
            print(f"  Confidence: {self.latest_activity.confidence:.1%}")

        print("\n" + "=" * 70)
        print("Press Ctrl+C to exit")

    @staticmethod
    def make_bar(value: float, min_val: float, max_val: float, width: int = 40) -> str:
        """Create a text-based bar chart"""
        # Normalize value to 0-1 range
        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0, min(1, normalized))  # Clamp to 0-1

        # Calculate bar position
        pos = int(normalized * width)

        # Create bar with center marker
        center = width // 2
        bar = ['-'] * width
        bar[center] = '|'  # Center line

        if pos < center:
            for i in range(pos, center):
                bar[i] = '◀'
        elif pos > center:
            for i in range(center + 1, pos + 1):
                bar[i] = '▶'
        else:
            bar[center] = '●'

        return ''.join(bar)

    async def start(self):
        """Start the viewer"""
        print("\n" + "=" * 70)
        print("        APPLE WATCH SENSOR VIEWER")
        print("=" * 70)
        print("\nStarting server...")

        # Print QR code for connection
        self.server.print_qr_code()

        print("\n📱 Instructions:")
        print("  1. Open Arvos app on iPhone")
        print("  2. Make sure Apple Watch is paired and companion app installed")
        print("  3. Enable 'Apple Watch' toggle in Sensor Test or Settings")
        print("  4. Scan QR code or enter server IP manually")
        print("  5. Start streaming")
        print("\nWaiting for connection...\n")

        # Start server
        await self.server.start()


async def main():
    """Main entry point"""
    viewer = WatchSensorViewer()

    try:
        await viewer.start()
    except KeyboardInterrupt:
        print("\n\n✅ Viewer stopped")

        # Print final statistics
        if viewer.imu_count > 0:
            uptime = time.time() - viewer.start_time if viewer.start_time else 0
            print(f"\n📊 Final Statistics:")
            print(f"  Total runtime: {uptime:.1f}s")
            print(f"  IMU samples: {viewer.imu_count}")
            print(f"  Attitude samples: {viewer.attitude_count}")
            print(f"  Activity updates: {viewer.activity_count}")

            if uptime > 0:
                print(f"  Average IMU rate: {viewer.imu_count / uptime:.1f} Hz")


if __name__ == "__main__":
    asyncio.run(main())
