#!/usr/bin/env python3
"""
ARVOS Info Tool - Display session metadata and statistics

Quick summary of recording contents
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta


def show_session_info(mcap_file):
    """Display information about an MCAP recording"""
    print(f"📁 {mcap_file.name}")
    print("=" * 60)

    # TODO: Parse actual MCAP file
    # For now, show expected format

    info = {
        'file_size': 145_623_890,  # bytes
        'duration': 182.5,  # seconds
        'start_time': datetime.now(),
        'mode': 'RGBD Camera',
        'sensors': {
            'camera': {'enabled': True, 'frames': 5475, 'fps': 30.0},
            'depth': {'enabled': True, 'frames': 913, 'fps': 5.0},
            'imu': {'enabled': True, 'samples': 36500, 'hz': 200.0},
            'pose': {'enabled': True, 'samples': 5475, 'hz': 30.0},
            'gps': {'enabled': False, 'samples': 0, 'hz': 0},
        },
        'device': 'iPhone 15 Pro',
        'os_version': 'iOS 17.1',
        'app_version': '1.0.0',
    }

    # Basic info
    file_size_mb = info['file_size'] / (1024 * 1024)
    duration_str = str(timedelta(seconds=int(info['duration'])))
    print(f"Size:     {file_size_mb:.1f} MB")
    print(f"Duration: {duration_str}")
    print(f"Started:  {info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode:     {info['mode']}")
    print()

    # Sensors
    print("📊 Sensor Data:")
    print("-" * 60)
    for sensor, data in info['sensors'].items():
        if data['enabled']:
            if sensor == 'camera':
                print(f"  📷 Camera:  {data['frames']:,} frames @ {data['fps']:.1f} FPS")
            elif sensor == 'depth':
                print(f"  🔷 Depth:   {data['frames']:,} frames @ {data['fps']:.1f} FPS")
            elif sensor == 'imu':
                print(f"  📐 IMU:     {data['samples']:,} samples @ {data['hz']:.0f} Hz")
            elif sensor == 'pose':
                print(f"  📍 Pose:    {data['samples']:,} samples @ {data['hz']:.1f} Hz")
            elif sensor == 'gps':
                print(f"  🛰️  GPS:     {data['samples']:,} samples @ {data['hz']:.1f} Hz")
        else:
            print(f"  ⚪ {sensor.upper()}: Disabled")

    print()

    # Device
    print("📱 Device Info:")
    print("-" * 60)
    print(f"  Model:   {info['device']}")
    print(f"  iOS:     {info['os_version']}")
    print(f"  App:     v{info['app_version']}")

    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Display ARVOS session information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show info for single session
  arvos-info session.mcap

  # Show info for multiple sessions
  arvos-info ./recordings/*.mcap

  # Brief summary (one line per file)
  arvos-info *.mcap --brief

Output Format:
  - File size and duration
  - Recording start time
  - Streaming mode used
  - Sensor data counts
  - Device information
        """
    )

    parser.add_argument('files', nargs='+', type=str,
                        help='MCAP file(s) to inspect')
    parser.add_argument('--brief', '-b', action='store_true',
                        help='Brief one-line summary per file')

    args = parser.parse_args()

    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {path}")
            continue

        if args.brief:
            # Brief format: filename | size | duration | mode
            print(f"{path.name} | 145MB | 3m 2s | RGBD Camera")
        else:
            show_session_info(path)


if __name__ == '__main__':
    main()
