#!/usr/bin/env python3
"""
ROS 2 Bridge for Arvos

This bridge converts Arvos sensor data to ROS 2 topics.

Requirements:
    - ROS 2 (Humble, Iron, or newer)
    - pip install opencv-python numpy

Topics published:
    /arvos/imu              - sensor_msgs/Imu
    /arvos/gps              - sensor_msgs/NavSatFix
    /arvos/camera/image_raw - sensor_msgs/Image
    /arvos/camera/info      - sensor_msgs/CameraInfo
    /arvos/depth/points     - sensor_msgs/PointCloud2
    /arvos/tf               - tf2_msgs/TFMessage

Usage:
    python ros2_bridge.py
"""

import asyncio
import threading
import numpy as np

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Imu, NavSatFix, Image, CameraInfo, PointCloud2, PointField
    from geometry_msgs.msg import TransformStamped
    from std_msgs.msg import Header
    from tf2_ros import TransformBroadcaster
    import cv2
    from cv_bridge import CvBridge
except ImportError:
    print("Error: This example requires ROS 2")
    print("Make sure ROS 2 is sourced and cv_bridge is installed")
    exit(1)

from arvos import ArvosServer, IMUData, GPSData, PoseData, CameraFrame, DepthFrame


class ArvosROS2Bridge(Node):
    def __init__(self):
        super().__init__('arvos_bridge')

        # Publishers
        self.imu_pub = self.create_publisher(Imu, '/arvos/imu', 10)
        self.gps_pub = self.create_publisher(NavSatFix, '/arvos/gps', 10)
        self.image_pub = self.create_publisher(Image, '/arvos/camera/image_raw', 10)
        self.camera_info_pub = self.create_publisher(CameraInfo, '/arvos/camera/info', 10)
        self.points_pub = self.create_publisher(PointCloud2, '/arvos/depth/points', 10)

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # CV Bridge
        self.bridge = CvBridge()

        self.get_logger().info('Arvos ROS 2 Bridge initialized')

    def publish_imu(self, data: IMUData):
        """Publish IMU data"""
        msg = Imu()
        msg.header = Header()
        msg.header.stamp = self.timestamp_to_ros(data.timestamp_ns)
        msg.header.frame_id = 'arvos_imu'

        # Angular velocity
        msg.angular_velocity.x = data.angular_velocity[0]
        msg.angular_velocity.y = data.angular_velocity[1]
        msg.angular_velocity.z = data.angular_velocity[2]

        # Linear acceleration
        msg.linear_acceleration.x = data.linear_acceleration[0]
        msg.linear_acceleration.y = data.linear_acceleration[1]
        msg.linear_acceleration.z = data.linear_acceleration[2]

        # Orientation (if available)
        if data.attitude:
            # Convert roll, pitch, yaw to quaternion
            roll, pitch, yaw = data.attitude
            cy = np.cos(yaw * 0.5)
            sy = np.sin(yaw * 0.5)
            cp = np.cos(pitch * 0.5)
            sp = np.sin(pitch * 0.5)
            cr = np.cos(roll * 0.5)
            sr = np.sin(roll * 0.5)

            msg.orientation.w = cr * cp * cy + sr * sp * sy
            msg.orientation.x = sr * cp * cy - cr * sp * sy
            msg.orientation.y = cr * sp * cy + sr * cp * sy
            msg.orientation.z = cr * cp * sy - sr * sp * cy

        self.imu_pub.publish(msg)

    def publish_gps(self, data: GPSData):
        """Publish GPS data"""
        msg = NavSatFix()
        msg.header = Header()
        msg.header.stamp = self.timestamp_to_ros(data.timestamp_ns)
        msg.header.frame_id = 'arvos_gps'

        msg.latitude = data.latitude
        msg.longitude = data.longitude
        msg.altitude = data.altitude

        # Covariance
        msg.position_covariance[0] = data.horizontal_accuracy ** 2
        msg.position_covariance[4] = data.horizontal_accuracy ** 2
        msg.position_covariance[8] = data.vertical_accuracy ** 2
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN

        self.gps_pub.publish(msg)

    def publish_pose(self, data: PoseData):
        """Publish pose as TF transform"""
        t = TransformStamped()
        t.header = Header()
        t.header.stamp = self.timestamp_to_ros(data.timestamp_ns)
        t.header.frame_id = 'world'
        t.child_frame_id = 'arvos_camera'

        # Translation
        t.transform.translation.x = float(data.position[0])
        t.transform.translation.y = float(data.position[1])
        t.transform.translation.z = float(data.position[2])

        # Rotation (quaternion)
        t.transform.rotation.x = float(data.orientation[0])
        t.transform.rotation.y = float(data.orientation[1])
        t.transform.rotation.z = float(data.orientation[2])
        t.transform.rotation.w = float(data.orientation[3])

        self.tf_broadcaster.sendTransform(t)

    def publish_camera(self, frame: CameraFrame):
        """Publish camera image"""
        # Decode JPEG
        try:
            import io
            from PIL import Image as PILImage
            image = PILImage.open(io.BytesIO(frame.data))
            img_array = np.array(image)

            # Convert to ROS message
            msg = self.bridge.cv2_to_imgmsg(img_array, encoding='rgb8')
            msg.header.stamp = self.timestamp_to_ros(frame.timestamp_ns)
            msg.header.frame_id = 'arvos_camera'

            self.image_pub.publish(msg)

            # Publish camera info
            if frame.intrinsics:
                info_msg = CameraInfo()
                info_msg.header = msg.header
                info_msg.width = frame.width
                info_msg.height = frame.height

                # Intrinsic matrix
                info_msg.k = [
                    frame.intrinsics.fx, 0.0, frame.intrinsics.cx,
                    0.0, frame.intrinsics.fy, frame.intrinsics.cy,
                    0.0, 0.0, 1.0
                ]

                # Distortion (assuming no distortion)
                info_msg.d = [0.0, 0.0, 0.0, 0.0, 0.0]
                info_msg.distortion_model = 'plumb_bob'

                # Projection matrix
                info_msg.p = [
                    frame.intrinsics.fx, 0.0, frame.intrinsics.cx, 0.0,
                    0.0, frame.intrinsics.fy, frame.intrinsics.cy, 0.0,
                    0.0, 0.0, 1.0, 0.0
                ]

                self.camera_info_pub.publish(info_msg)

        except Exception as e:
            self.get_logger().error(f"Failed to publish camera: {e}")

    def publish_depth(self, frame: DepthFrame):
        """Publish point cloud"""
        try:
            # Parse point cloud
            points = frame.to_point_cloud()
            if points is None:
                return

            # Create PointCloud2 message
            msg = PointCloud2()
            msg.header = Header()
            msg.header.stamp = self.timestamp_to_ros(frame.timestamp_ns)
            msg.header.frame_id = 'arvos_camera'

            msg.height = 1
            msg.width = len(points)

            # Define fields
            msg.fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
                PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1)
            ]

            msg.is_bigendian = False
            msg.point_step = 16
            msg.row_step = msg.point_step * msg.width
            msg.is_dense = True

            # Pack data
            cloud_data = []
            for point in points:
                x, y, z = point[:3]
                if len(point) >= 6:
                    r, g, b = point[3:6].astype(np.uint8)
                    rgb = (int(r) << 16) | (int(g) << 8) | int(b)
                else:
                    rgb = 0xFFFFFF

                cloud_data.append(struct.pack('fffI', x, y, z, rgb))

            msg.data = b''.join(cloud_data)

            self.points_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(f"Failed to publish point cloud: {e}")

    def timestamp_to_ros(self, timestamp_ns: int):
        """Convert nanosecond timestamp to ROS time"""
        from rclpy.time import Time
        return Time(nanoseconds=timestamp_ns).to_msg()


async def run_arvos_server(bridge):
    """Run Arvos WebSocket server"""
    server = ArvosServer(port=9090)

    # Connect callbacks to ROS bridge
    server.on_imu = lambda data: bridge.publish_imu(data)
    server.on_gps = lambda data: bridge.publish_gps(data)
    server.on_pose = lambda data: bridge.publish_pose(data)
    server.on_camera = lambda data: bridge.publish_camera(data)
    server.on_depth = lambda data: bridge.publish_depth(data)

    async def on_connect(client_id: str):
        bridge.get_logger().info(f"Client connected: {client_id}")

    async def on_disconnect(client_id: str):
        bridge.get_logger().info(f"Client disconnected: {client_id}")

    server.on_connect = on_connect
    server.on_disconnect = on_disconnect

    await server.start()


def main():
    # Initialize ROS 2
    rclpy.init()

    # Create bridge node
    bridge = ArvosROS2Bridge()

    # Run Arvos server in separate thread
    loop = asyncio.new_event_loop()

    def run_async():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_arvos_server(bridge))

    server_thread = threading.Thread(target=run_async, daemon=True)
    server_thread.start()

    # Spin ROS node
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    finally:
        bridge.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
