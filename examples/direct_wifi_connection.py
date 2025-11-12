#!/usr/bin/env python3
"""
Direct WiFi Connection Example
Connect directly to iPhone's Personal Hotspot for lower latency streaming

When connected to iPhone's hotspot:
- iPhone's IP is typically 172.20.10.1
- Your computer gets an IP like 172.20.10.2, 172.20.10.3, etc.
- Lower latency than going through a router
- Works anywhere without WiFi network

Setup:
1. Enable Personal Hotspot on iPhone (Settings → Personal Hotspot → ON)
2. Connect your computer to iPhone's hotspot
3. Run this script
4. Start streaming from iPhone ARVOS app
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arvos import ArvosServer
from arvos.data_types import IMUData, GPSData, PoseData, CameraFrame, DepthFrame
import socket


def get_hotspot_info():
    """
    Detect if connected to iPhone hotspot and get network info.
    
    Returns:
        tuple: (is_hotspot, iphone_ip, computer_ip)
    """
    try:
        # Get computer's IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        computer_ip = s.getsockname()[0]
        s.close()
        
        # Check if IP is in hotspot range (172.20.10.x)
        is_hotspot = computer_ip.startswith("172.20.10.")
        iphone_ip = "172.20.10.1" if is_hotspot else None
        
        return is_hotspot, iphone_ip, computer_ip
    except Exception as e:
        print(f"Error detecting hotspot: {e}")
        return False, None, None


def print_connection_info():
    """Print connection information and setup instructions."""
    is_hotspot, iphone_ip, computer_ip = get_hotspot_info()
    
    print("\n" + "="*60)
    print("ARVOS Direct WiFi Connection")
    print("="*60)
    
    if is_hotspot:
        print("✅ Connected to iPhone Personal Hotspot!")
        print(f"\nYour computer IP: {computer_ip}")
        print(f"iPhone IP: {iphone_ip}")
        print(f"\nServer will listen on: ws://0.0.0.0:9090")
        print(f"iPhone should connect to: ws://{computer_ip}:9090")
    else:
        print("⚠️  Not connected to iPhone Personal Hotspot")
        print(f"\nYour computer IP: {computer_ip}")
        print("\nTo use Direct WiFi Connection:")
        print("1. Enable Personal Hotspot on iPhone")
        print("2. Connect your computer to iPhone's hotspot")
        print("3. Run this script again")
        print("\nContinuing with regular WiFi connection...")
    
    print("="*60 + "\n")


async def main():
    """Main entry point."""
    
    # Print connection info
    print_connection_info()
    
    # Create server
    server = ArvosServer(host="0.0.0.0", port=9090)
    
    # Setup callbacks
    async def on_connect(client_id: str):
        print(f"✅ iPhone connected: {client_id}")
        print(f"🚀 Direct WiFi streaming active!")
    
    async def on_disconnect(client_id: str):
        print(f"📱 iPhone disconnected: {client_id}")
    
    async def on_imu(data: IMUData):
        accel = data.linear_acceleration
        gyro = data.angular_velocity
        print(f"📊 IMU: accel=({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f}) "
              f"gyro=({gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f})")
    
    async def on_gps(data: GPSData):
        print(f"📍 GPS: ({data.latitude:.6f}, {data.longitude:.6f}) "
              f"accuracy=±{data.horizontal_accuracy:.1f}m")
    
    async def on_pose(data: PoseData):
        pos = data.position
        print(f"📐 Pose: position=({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) "
              f"tracking={data.tracking_state}")
    
    async def on_camera(frame: CameraFrame):
        print(f"📷 Camera: {frame.width}x{frame.height} {frame.size_kb:.1f}KB")
    
    async def on_depth(frame: DepthFrame):
        print(f"🔵 Depth: {frame.point_count} points, "
              f"range={frame.min_depth:.1f}m-{frame.max_depth:.1f}m")
    
    # Assign callbacks
    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_camera = on_camera
    server.on_depth = on_depth
    
    # Print QR code for easy connection
    print("Scan this QR code with iPhone:")
    server.print_qr_code()
    
    print("\n💡 Benefits of Direct WiFi Connection:")
    print("  • Lower latency (no router hop)")
    print("  • Higher throughput")
    print("  • Works anywhere (no WiFi network needed)")
    print("  • More secure (direct device-to-device)")
    
    print("\n🚀 Starting server...")
    print("Press Ctrl+C to stop\n")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())

