import asyncio
from arvos import ArvosServer

async def main():
    server = ArvosServer(port=9090)

    # Show QR code for easy connection
    server.print_qr_code()

    # Define callbacks
    async def on_imu(data):
        print(f"IMU: accel={data.linear_acceleration}")

    server.on_imu = on_imu

    await server.start()

asyncio.run(main())