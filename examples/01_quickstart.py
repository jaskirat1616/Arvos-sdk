#!/usr/bin/env python3
"""
ARVOS Quickstart Example
Connect to iPhone and print sensor data in 5 lines
"""

import asyncio
from arvos import ArvosServer

async def main():
    # Create server
    server = ArvosServer(port=8765)

    # Simple callback to print data
    @server.on_imu
    def handle_imu(data):
        print(f"IMU: {data.linear_acceleration}")

    @server.on_pose
    def handle_pose(data):
        print(f"Pose: {data.position}")

    # Start server
    await server.start()

if __name__ == "__main__":
    print("🚀 ARVOS Quickstart")
    print("📱 Connect your iPhone ARVOS app to see data")
    print()
    asyncio.run(main())
