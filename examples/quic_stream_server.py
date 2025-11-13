#!/usr/bin/env python3
"""
Example QUIC/HTTP3 server for receiving sensor data from the ARVOS iOS app.

Note: QUIC/HTTP3 requires TLS certificates. For local development, generate
self-signed certificates:

    openssl req -x509 -newkey rsa:2048 -keyout /tmp/arvos-quic.key \\
        -out /tmp/arvos-quic-cert.pem -days 365 -nodes

Then install the certificate on your iPhone for testing.

Requirements:
    pip install aioquic
"""

import asyncio
import sys

try:
    from arvos.servers import QUICArvosServer
except ImportError:
    print("❌ aioquic is required for QUIC/HTTP3 support.")
    print("   Install it with: pip install aioquic")
    sys.exit(1)

from arvos.data_types import IMUData, GPSData, PoseData


async def main():
    # Generate certificates if needed
    import os
    from pathlib import Path
    
    certfile = "/tmp/arvos-quic-cert.pem"
    keyfile = "/tmp/arvos-quic.key"
    
    if not Path(certfile).exists():
        print("⚠️  Self-signed certificate not found.")
        print("   Generating certificate...")
        os.system(
            f"openssl req -x509 -newkey rsa:2048 -keyout {keyfile} "
            f"-out {certfile} -days 365 -nodes -subj '/CN=localhost'"
        )
        print(f"✅ Certificate generated: {certfile}")
        print("   Note: You may need to install this certificate on your iPhone for testing.\n")
    
    server = QUICArvosServer(
        host="0.0.0.0",
        port=4433,
        certfile=certfile,
        keyfile=keyfile
    )

    async def on_connect(client_id: str):
        print(f"✅ QUIC/HTTP3 client connected: {client_id}")

    async def on_disconnect(client_id: str):
        print(f"👋 QUIC/HTTP3 client disconnected: {client_id}")

    def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration} gyro={data.angular_velocity}")

    def on_gps(data: GPSData):
        print(f"📍 GPS: lat={data.latitude:.6f}, lon={data.longitude:.6f}, accuracy ±{data.horizontal_accuracy:.1f}m")

    def on_pose(data: PoseData):
        print(f"🧭 Pose: position={data.position} tracking={data.tracking_state}")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose

    server.print_connection_info()
    print("Waiting for QUIC/HTTP3 sensor data... Press Ctrl+C to stop.")
    print("\n⚠️  Note: iOS requires valid TLS certificates for HTTP/3.")
    print("   For local testing, install the self-signed certificate on your iPhone.\n")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())

