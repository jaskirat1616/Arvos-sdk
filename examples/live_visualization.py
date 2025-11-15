#!/usr/bin/env python3
"""
Live visualization of sensor data using matplotlib

This example creates real-time plots of IMU and pose data.

Requirements:
    pip install matplotlib numpy

Usage:
    python live_visualization.py
"""

import asyncio
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from arvos import ArvosServer, IMUData, PoseData
import numpy as np


class SensorVisualizer:
    def __init__(self, history_length=100):
        self.history_length = history_length

        # Data buffers
        self.imu_times = deque(maxlen=history_length)
        self.acc_x = deque(maxlen=history_length)
        self.acc_y = deque(maxlen=history_length)
        self.acc_z = deque(maxlen=history_length)
        self.gyro_x = deque(maxlen=history_length)
        self.gyro_y = deque(maxlen=history_length)
        self.gyro_z = deque(maxlen=history_length)

        self.pose_times = deque(maxlen=history_length)
        self.pos_x = deque(maxlen=history_length)
        self.pos_y = deque(maxlen=history_length)
        self.pos_z = deque(maxlen=history_length)

        # Create figure
        self.fig, self.axes = plt.subplots(3, 1, figsize=(12, 8))
        self.fig.suptitle('Arvos Live Sensor Data', fontsize=16)

        # Acceleration plot
        self.ax_acc = self.axes[0]
        self.ax_acc.set_title('Linear Acceleration (m/s²)')
        self.ax_acc.set_ylabel('Acceleration')
        self.ax_acc.grid(True)
        self.line_acc_x, = self.ax_acc.plot([], [], 'r-', label='X')
        self.line_acc_y, = self.ax_acc.plot([], [], 'g-', label='Y')
        self.line_acc_z, = self.ax_acc.plot([], [], 'b-', label='Z')
        self.ax_acc.legend(loc='upper right')

        # Gyroscope plot
        self.ax_gyro = self.axes[1]
        self.ax_gyro.set_title('Angular Velocity (rad/s)')
        self.ax_gyro.set_ylabel('Angular Velocity')
        self.ax_gyro.grid(True)
        self.line_gyro_x, = self.ax_gyro.plot([], [], 'r-', label='X')
        self.line_gyro_y, = self.ax_gyro.plot([], [], 'g-', label='Y')
        self.line_gyro_z, = self.ax_gyro.plot([], [], 'b-', label='Z')
        self.ax_gyro.legend(loc='upper right')

        # Position plot
        self.ax_pos = self.axes[2]
        self.ax_pos.set_title('Position (m)')
        self.ax_pos.set_xlabel('Time (s)')
        self.ax_pos.set_ylabel('Position')
        self.ax_pos.grid(True)
        self.line_pos_x, = self.ax_pos.plot([], [], 'r-', label='X')
        self.line_pos_y, = self.ax_pos.plot([], [], 'g-', label='Y')
        self.line_pos_z, = self.ax_pos.plot([], [], 'b-', label='Z')
        self.ax_pos.legend(loc='upper right')

        plt.tight_layout()

    def update_imu(self, data: IMUData):
        """Update IMU data"""
        self.imu_times.append(data.timestamp_s)
        self.acc_x.append(data.linear_acceleration[0])
        self.acc_y.append(data.linear_acceleration[1])
        self.acc_z.append(data.linear_acceleration[2])
        self.gyro_x.append(data.angular_velocity[0])
        self.gyro_y.append(data.angular_velocity[1])
        self.gyro_z.append(data.angular_velocity[2])

    def update_pose(self, data: PoseData):
        """Update pose data"""
        self.pose_times.append(data.timestamp_s)
        self.pos_x.append(data.position[0])
        self.pos_y.append(data.position[1])
        self.pos_z.append(data.position[2])

    def animate(self, frame):
        """Animation update function"""
        if len(self.imu_times) > 0:
            # Normalize timestamps
            imu_times = np.array(self.imu_times) - self.imu_times[0]

            # Update acceleration plot
            self.line_acc_x.set_data(imu_times, self.acc_x)
            self.line_acc_y.set_data(imu_times, self.acc_y)
            self.line_acc_z.set_data(imu_times, self.acc_z)
            self.ax_acc.relim()
            self.ax_acc.autoscale_view()

            # Update gyroscope plot
            self.line_gyro_x.set_data(imu_times, self.gyro_x)
            self.line_gyro_y.set_data(imu_times, self.gyro_y)
            self.line_gyro_z.set_data(imu_times, self.gyro_z)
            self.ax_gyro.relim()
            self.ax_gyro.autoscale_view()

        if len(self.pose_times) > 0:
            # Normalize timestamps
            pose_times = np.array(self.pose_times) - self.pose_times[0]

            # Update position plot
            self.line_pos_x.set_data(pose_times, self.pos_x)
            self.line_pos_y.set_data(pose_times, self.pos_y)
            self.line_pos_z.set_data(pose_times, self.pos_z)
            self.ax_pos.relim()
            self.ax_pos.autoscale_view()

        return (self.line_acc_x, self.line_acc_y, self.line_acc_z,
                self.line_gyro_x, self.line_gyro_y, self.line_gyro_z,
                self.line_pos_x, self.line_pos_y, self.line_pos_z)


async def run_server(visualizer):
    """Run Arvos server"""
    server = ArvosServer(port=9090)

    server.on_imu = lambda data: visualizer.update_imu(data)
    server.on_pose = lambda data: visualizer.update_pose(data)

    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}")
        print("📊 Visualization starting...")

    server.on_connect = on_connect

    await server.start()


def main():
    print("🚀 Starting Arvos live visualization...")
    print("📱 Connect your iPhone to see real-time sensor plots")

    # Create visualizer
    visualizer = SensorVisualizer()

    # Start server in background
    loop = asyncio.new_event_loop()

    def run_async():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server(visualizer))

    import threading
    server_thread = threading.Thread(target=run_async, daemon=True)
    server_thread.start()

    # Run matplotlib animation
    ani = animation.FuncAnimation(
        visualizer.fig,
        visualizer.animate,
        interval=50,  # 20 FPS
        blit=True
    )

    plt.show()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Visualization stopped")
