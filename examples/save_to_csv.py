#!/usr/bin/env python3
"""
Save sensor data to CSV files

This example saves IMU, GPS, and pose data to separate CSV files
for later analysis.

Usage:
    python save_to_csv.py
"""

import asyncio
import csv
from datetime import datetime
from pathlib import Path
from arvos import ArvosServer, IMUData, GPSData, PoseData


async def main():
    # Create output directory
    output_dir = Path(f"arvos_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)

    print(f"📁 Saving data to: {output_dir}")

    # Create CSV files
    imu_file = open(output_dir / "imu.csv", "w", newline="")
    gps_file = open(output_dir / "gps.csv", "w", newline="")
    pose_file = open(output_dir / "pose.csv", "w", newline="")

    # Create CSV writers
    imu_writer = csv.writer(imu_file)
    imu_writer.writerow([
        "timestamp_ns", "timestamp_s",
        "ang_vel_x", "ang_vel_y", "ang_vel_z",
        "lin_acc_x", "lin_acc_y", "lin_acc_z",
        "roll", "pitch", "yaw"
    ])

    gps_writer = csv.writer(gps_file)
    gps_writer.writerow([
        "timestamp_ns", "timestamp_s",
        "latitude", "longitude", "altitude",
        "h_accuracy", "v_accuracy", "speed", "course"
    ])

    pose_writer = csv.writer(pose_file)
    pose_writer.writerow([
        "timestamp_ns", "timestamp_s",
        "pos_x", "pos_y", "pos_z",
        "quat_x", "quat_y", "quat_z", "quat_w",
        "tracking_state"
    ])

    server = ArvosServer(port=9090)

    # Handle IMU data
    async def on_imu(data: IMUData):
        imu_writer.writerow([
            data.timestamp_ns, data.timestamp_s,
            *data.angular_velocity,
            *data.linear_acceleration,
            *data.attitude if data.attitude else (0, 0, 0)
        ])

    # Handle GPS data
    async def on_gps(data: GPSData):
        gps_writer.writerow([
            data.timestamp_ns, data.timestamp_s,
            data.latitude, data.longitude, data.altitude,
            data.horizontal_accuracy, data.vertical_accuracy,
            data.speed, data.course
        ])

    # Handle pose data
    async def on_pose(data: PoseData):
        pose_writer.writerow([
            data.timestamp_ns, data.timestamp_s,
            *data.position,
            *data.orientation,
            data.tracking_state
        ])

    # Handle disconnection
    async def on_disconnect(client_id: str):
        print(f"\n💾 Flushing and closing CSV files...")
        imu_file.close()
        gps_file.close()
        pose_file.close()
        print(f"✅ Data saved to {output_dir}")

    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_disconnect = on_disconnect

    print("🚀 Starting server...")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
        imu_file.close()
        gps_file.close()
        pose_file.close()


if __name__ == "__main__":
    asyncio.run(main())
