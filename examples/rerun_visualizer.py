#!/usr/bin/env python3
"""
Full Arvos sensor visualization powered by Rerun (https://rerun.io/).

This script starts an `ArvosServer`, listens for every sensor payload the iPhone
app can deliver, and mirrors it live into a Rerun viewer. It is a quick way to
explore IMU, GPS, pose, camera, depth, and Apple Watch data streams without
building your own UI.

Usage:
    pip install rerun-sdk pillow
    python examples/rerun_visualizer.py --port 9090

Features:
    * Launches/attaches to a Rerun viewer (spawned locally by default)
    * Logs device handshake & capability metadata
    * Streams IMU and Watch IMU scalars
    * Tracks GPS positions and pose trajectories
    * Visualizes camera frames (auto-decodes JPEG with Pillow when available)
    * Streams LiDAR/scene depth as 3D point clouds

To share the visualization to a remote viewer, use `--viewer ws://...`.
"""

from __future__ import annotations

import argparse
import asyncio
from collections import deque
from typing import Any, Deque, Optional, Tuple

import numpy as np
import rerun as rr

from arvos import ArvosServer
from arvos.data_types import (
    CameraFrame,
    DepthFrame,
    GPSData,
    HandshakeMessage,
    IMUData,
    PoseData,
)

try:  # Apple Watch data types are optional in some installations
    from arvos.data_types import (  # type: ignore[attr-defined]
        WatchAttitudeData,
        WatchIMUData,
        WatchMotionActivityData,
    )
except ImportError:  # pragma: no cover - fallback for older builds
    WatchIMUData = WatchAttitudeData = WatchMotionActivityData = Any  # type: ignore[misc,assignment]


class RerunArvosVisualizer:
    """Bridge Arvos sensor streams into a Rerun viewer."""

    def __init__(
        self,
        *,
        port: int,
        app_id: str = "arvos_rerun_demo",
        spawn_viewer: bool = True,
        viewer_url: Optional[str] = None,
        max_history: int = 2048,
    ) -> None:
        self.server = ArvosServer(port=port)
        self.server.on_connect = self.on_connect
        self.server.on_disconnect = self.on_disconnect
        self.server.on_handshake = self.on_handshake
        self.server.on_status = self.on_status
        self.server.on_error = self.on_error
        self.server.on_imu = self.on_imu
        self.server.on_gps = self.on_gps
        self.server.on_pose = self.on_pose
        self.server.on_camera = self.on_camera
        self.server.on_depth = self.on_depth
        self.server.on_watch_imu = self.on_watch_imu
        self.server.on_watch_attitude = self.on_watch_attitude
        self.server.on_watch_activity = self.on_watch_activity

        self.pose_history: Deque[Tuple[float, float, float]] = deque(maxlen=max_history)
        self.gps_history: Deque[Tuple[float, float]] = deque(maxlen=max_history)

        rr.init(app_id, spawn=spawn_viewer)
        if viewer_url:
            rr.connect(viewer_url)
        else:
            rr.connect()

        # Set a consistent world basis to make pose/depth easier to interpret.
        rr.log("world", rr.ViewCoordinates.RDF, static=True)

    async def run(self) -> None:
        """Run until interrupted."""
        await self.server.start()

    async def on_connect(self, client_id: str) -> None:
        rr.log("status/events", rr.TextLog(f"Client connected: {client_id}"))

    async def on_disconnect(self, client_id: str) -> None:
        rr.log("status/events", rr.TextLog(f"Client disconnected: {client_id}"))

    def on_handshake(self, handshake: HandshakeMessage) -> None:
        rr.log(
            "device/info",
            rr.TextLog(
                f"{handshake.device_name} ({handshake.device_model}) • iOS {handshake.os_version} • app {handshake.app_version}"
            ),
        )
        rr.log(
            "device/capabilities",
            rr.TextLog(
                f"LiDAR: {handshake.capabilities.has_lidar}, "
                f"ARKit: {handshake.capabilities.has_arkit}, "
                f"GPS: {handshake.capabilities.has_gps}, "
                f"IMU: {handshake.capabilities.has_imu}, "
                f"Modes: {', '.join(handshake.capabilities.supported_modes) or 'n/a'}"
            ),
        )

    def on_status(self, status: dict) -> None:
        rr.log("status/messages", rr.TextLog(str(status)))

    def on_error(self, error: Optional[str], details: Optional[str]) -> None:
        message = error or "unknown error"
        if details:
            message = f"{message} — {details}"
        rr.log("status/errors", rr.TextLog(message))

    async def on_imu(self, data: IMUData) -> None:
        rr.log_scalar("sensors/imu/angular_velocity/x", data.angular_velocity[0])
        rr.log_scalar("sensors/imu/angular_velocity/y", data.angular_velocity[1])
        rr.log_scalar("sensors/imu/angular_velocity/z", data.angular_velocity[2])
        rr.log_scalar("sensors/imu/linear_acceleration/x", data.linear_acceleration[0])
        rr.log_scalar("sensors/imu/linear_acceleration/y", data.linear_acceleration[1])
        rr.log_scalar("sensors/imu/linear_acceleration/z", data.linear_acceleration[2])
        if data.attitude:
            rr.log_scalar("sensors/imu/attitude/roll", data.attitude[0])
            rr.log_scalar("sensors/imu/attitude/pitch", data.attitude[1])
            rr.log_scalar("sensors/imu/attitude/yaw", data.attitude[2])
        if data.magnetic_field:
            rr.log_scalar("sensors/imu/magnetic/x", data.magnetic_field[0])
            rr.log_scalar("sensors/imu/magnetic/y", data.magnetic_field[1])
            rr.log_scalar("sensors/imu/magnetic/z", data.magnetic_field[2])

    async def on_gps(self, data: GPSData) -> None:
        rr.log_scalar("sensors/gps/latitude_deg", data.latitude)
        rr.log_scalar("sensors/gps/longitude_deg", data.longitude)
        rr.log_scalar("sensors/gps/altitude_m", data.altitude)
        self.gps_history.append((data.longitude, data.latitude))
        if len(self.gps_history) > 1:
            rr.log(
                "sensors/gps/track",
                rr.LineStrips2D([np.array(self.gps_history, dtype=np.float32)]),
            )

    async def on_pose(self, data: PoseData) -> None:
        translation = np.array(data.position, dtype=np.float32)
        self.pose_history.append(tuple(translation))
        rr.log(
            "pose/camera",
            rr.Transform3D(
                translation=translation,
                rotation=rr.Quaternion(xyzw=np.array(data.orientation, dtype=np.float32)),
            ),
        )
        if len(self.pose_history) > 1:
            rr.log(
                "pose/trajectory",
                rr.LineStrips3D([np.array(self.pose_history, dtype=np.float32)]),
            )

    async def on_camera(self, frame: CameraFrame) -> None:
        image_array = frame.to_numpy()
        if image_array is not None:
            rr.log("camera/image", rr.Image(image_array))
        else:
            rr.log(
                "camera/image_info",
                rr.TextLog(
                    f"{frame.format.upper()} frame ({frame.width}x{frame.height}, {frame.size_kb:.1f} KiB)"
                ),
            )

    async def on_depth(self, frame: DepthFrame) -> None:
        points = frame.to_point_cloud()
        if points is None:
            rr.log(
                "depth/info",
                rr.TextLog(
                    f"Depth frame ({frame.point_count} points, format={frame.format}, {frame.size_kb:.1f} KiB)"
                ),
            )
            return

        positions = points[:, :3].astype(np.float32, copy=False)
        colors = None
        if points.shape[1] >= 6:
            colors = (points[:, 3:6].astype(np.float32, copy=False) / 255.0).clip(0.0, 1.0)

        rr.log("depth/point_cloud", rr.Points3D(positions=positions, colors=colors))

    async def on_watch_imu(self, data: WatchIMUData) -> None:  # type: ignore[override]
        rr.log_scalar("watch/imu/angular_velocity/x", data.angular_velocity[0])
        rr.log_scalar("watch/imu/angular_velocity/y", data.angular_velocity[1])
        rr.log_scalar("watch/imu/angular_velocity/z", data.angular_velocity[2])
        rr.log_scalar("watch/imu/linear_acceleration/x", data.linear_acceleration[0])
        rr.log_scalar("watch/imu/linear_acceleration/y", data.linear_acceleration[1])
        rr.log_scalar("watch/imu/linear_acceleration/z", data.linear_acceleration[2])

    async def on_watch_attitude(self, data: WatchAttitudeData) -> None:  # type: ignore[override]
        rr.log_scalar("watch/attitude/pitch", data.pitch)
        rr.log_scalar("watch/attitude/roll", data.roll)
        rr.log_scalar("watch/attitude/yaw", data.yaw)

    async def on_watch_activity(self, data: WatchMotionActivityData) -> None:  # type: ignore[override]
        rr.log("watch/activity/state", rr.TextLog(f"{data.state} ({data.confidence:.2f})"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stream every Arvos sensor to a live Rerun viewer."
    )
    parser.add_argument("--port", type=int, default=9090, help="WebSocket port to host the Arvos server on.")
    parser.add_argument(
        "--viewer",
        type=str,
        default=None,
        help="Optional ws:// URL for an existing Rerun viewer (omit to spawn a local viewer).",
    )
    parser.add_argument(
        "--no-spawn",
        action="store_true",
        help="Do not spawn a viewer automatically (use with --viewer).",
    )
    parser.add_argument(
        "--app-id",
        type=str,
        default="arvos_rerun_demo",
        help="Name shown inside the Rerun viewer.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    visualizer = RerunArvosVisualizer(
        port=args.port,
        app_id=args.app_id,
        spawn_viewer=not args.no_spawn,
        viewer_url=args.viewer,
    )

    print("\n🎥 Rerun viewer ready. Scan the QR code to connect your iPhone.\n")
    await visualizer.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Rerun visualizer…")

