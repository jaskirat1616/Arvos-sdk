#!/usr/bin/env python3
"""
Subscribe to ARVOS Bluetooth LE telemetry using the bleak library.

Prerequisites:
    pip install bleak

Run this script, then on the iOS app select the Bluetooth LE protocol.
"""

import asyncio
import json
from typing import Optional, List

from bleak import BleakScanner, BleakClient

SERVICE_UUID = "5B6A38A0-2A0E-4A5F-8C96-5ED26F1935B8"
DATA_CHAR_UUID = "3E2E3101-0BC0-4B53-9CF0-9E9981F357F1"


class BLEBuffer:
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, chunk: bytes) -> List[bytes]:
        self.buffer.extend(chunk)
        messages: List[bytes] = []

        while len(self.buffer) >= 4:
            length = int.from_bytes(self.buffer[:4], "little")
            if len(self.buffer) < 4 + length:
                break
            payload = bytes(self.buffer[4 : 4 + length])
            del self.buffer[: 4 + length]
            messages.append(payload)
        return messages


async def main():
    print("🔍 Scanning for ARVOS BLE peripheral...")

    def matches_service(device, advertisement_data):
        uuids = advertisement_data.service_uuids or []
        return SERVICE_UUID.lower() in [uuid.lower() for uuid in uuids]

    device = await BleakScanner.find_device_by_filter(matches_service, timeout=10.0)
    if device is None:
        print("❌ Could not find ARVOS BLE peripheral. Make sure the app is advertising.")
        return

    print(f"✅ Found device: {device.name} ({device.address})")

    buffer = BLEBuffer()

    def notification_handler(_: int, data: bytearray):
        for message in buffer.feed(bytes(data)):
            try:
                decoded = message.decode("utf-8")
                try:
                    parsed = json.loads(decoded)
                    print(f"📨 JSON message: {json.dumps(parsed, indent=2)[:500]}")
                except json.JSONDecodeError:
                    print(f"📨 Text payload: {decoded}")
            except UnicodeDecodeError:
                print(f"📦 Binary payload ({len(message)} bytes) received (not decoded)")

    async with BleakClient(device) as client:
        print("🔗 Connected. Subscribing to telemetry...")
        await client.start_notify(DATA_CHAR_UUID, notification_handler)
        print("Listening for BLE notifications. Press Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await client.stop_notify(DATA_CHAR_UUID)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping BLE receiver.")


