#!/usr/bin/env python3
"""
Example that bridges ARVOS MQTT telemetry into Python callbacks.

Requires:
    pip install paho-mqtt

Ensure you have an MQTT broker running (e.g. `mosquitto -p 1883`).
"""

import asyncio
from arvos.servers import MQTTArvosServer
from arvos.data_types import IMUData, GPSData


async def main():
    server = MQTTArvosServer(host="localhost", port=1883)

    async def on_connect(client_id: str):
        print(f"✅ MQTT client connected: {client_id}")

    async def on_disconnect(client_id: str):
        print(f"👋 MQTT client disconnected: {client_id}")

    def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration} gyro={data.angular_velocity}")

    def on_gps(data: GPSData):
        print(f"📍 GPS: lat={data.latitude:.6f}, lon={data.longitude:.6f}, accuracy ±{data.horizontal_accuracy:.1f}m")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_imu = on_imu
    server.on_gps = on_gps

    server.print_connection_info()
    print("Listening for MQTT telemetry... Press Ctrl+C to stop.")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nStopping MQTT server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())


