#!/usr/bin/env python3
"""
Arvos Launch Script - ROS-like launcher

Launches all viewer processes simultaneously.
Each viewer is a separate process, avoiding asyncio+OpenCV conflicts.

Usage:
    python launch_all.py [--port 9090]
    python launch_all.py --camera-only
    python launch_all.py --no-gps
"""

import subprocess
import argparse
import time
import signal
import sys
import os

# Store process handles
processes = []

def signal_handler(sig, frame):
    """Clean shutdown on Ctrl+C"""
    print("\n🛑 Shutting down all viewers...")
    for p in processes:
        p.terminate()
    for p in processes:
        p.wait()
    print("👋 All viewers closed")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main():
    parser = argparse.ArgumentParser(description='Arvos Viewer Launcher')
    parser.add_argument('--port', type=int, default=9090, help='Server port')
    parser.add_argument('--camera-only', action='store_true', help='Launch only camera viewer')
    parser.add_argument('--no-gps', action='store_true', help='Skip GPS viewer')
    parser.add_argument('--no-depth', action='store_true', help='Skip depth viewer')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("🚀 Arvos Viewer Launcher")
    print(f"📡 Port: {args.port}\n")

    # Launch camera viewer (always)
    print("📷 Launching camera viewer...")
    camera_script = os.path.join(script_dir, 'camera_viewer.py')
    p_camera = subprocess.Popen(['python3', camera_script, '--port', str(args.port)])
    processes.append(p_camera)
    time.sleep(0.5)

    if not args.camera_only:
        # Launch depth viewer
        if not args.no_depth:
            print("🔵 Launching depth viewer...")
            depth_script = os.path.join(script_dir, 'depth_viewer.py')
            p_depth = subprocess.Popen(['python3', depth_script, '--port', str(args.port)])
            processes.append(p_depth)
            time.sleep(0.5)

        # Launch GPS viewer
        if not args.no_gps:
            print("🌍 Launching GPS viewer...")
            gps_script = os.path.join(script_dir, 'gps_viewer.py')
            p_gps = subprocess.Popen(['python3', gps_script, '--port', str(args.port)])
            processes.append(p_gps)

    print(f"\n✅ Launched {len(processes)} viewer(s)")
    print("📱 Connect your iPhone to port", args.port)
    print("Press Ctrl+C to stop all viewers\n")

    # Wait for all processes
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
