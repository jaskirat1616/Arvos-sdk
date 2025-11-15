#!/usr/bin/env python3
"""
Live MCAP viewer with camera and LiDAR visualization

Shows real-time:
- Camera feed (OpenCV window)
- LiDAR point cloud (Open3D window)
- GPS location
- IMU data
- Pose tracking

Requirements:
    pip install opencv-python open3d numpy
"""

import asyncio
import cv2
import numpy as np
import threading
from arvos.servers import MCAPHTTPServer
from arvos.data_types import IMUData, GPSData, PoseData


class LiveViewer:
    def __init__(self):
        self.latest_camera = None
        self.latest_depth = None
        self.latest_gps = None
        self.latest_imu = None
        self.latest_pose = None

        self.camera_lock = threading.Lock()
        self.depth_lock = threading.Lock()

        self.running = True
        self.frame_count = 0

    def update_camera(self, camera_frame):
        """Update camera frame"""
        try:
            # Decode JPEG data to OpenCV image
            img_array = np.frombuffer(camera_frame.data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is not None:
                with self.camera_lock:
                    self.latest_camera = img
                    self.frame_count += 1
        except Exception as e:
            print(f"Error decoding camera: {e}")

    def update_depth(self, depth_frame):
        """Update depth point cloud"""
        try:
            with self.depth_lock:
                self.latest_depth = depth_frame
        except Exception as e:
            print(f"Error updating depth: {e}")

    def update_gps(self, gps_data):
        """Update GPS data"""
        self.latest_gps = gps_data

    def update_imu(self, imu_data):
        """Update IMU data"""
        self.latest_imu = imu_data

    def update_pose(self, pose_data):
        """Update pose data"""
        self.latest_pose = pose_data

    def create_info_overlay(self, img):
        """Add info overlay to camera image"""
        if img is None:
            return None

        # Create a copy to draw on
        overlay = img.copy()
        h, w = overlay.shape[:2]

        # Semi-transparent background for text
        cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
        img_with_overlay = cv2.addWeighted(overlay, 0.3, img, 0.7, 0)

        y_offset = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (0, 255, 0)
        thickness = 1

        # Frame count
        cv2.putText(img_with_overlay, f"Frame: {self.frame_count}",
                    (20, y_offset), font, font_scale, color, thickness)
        y_offset += 25

        # GPS
        if self.latest_gps:
            gps_text = f"GPS: {self.latest_gps.latitude:.6f}, {self.latest_gps.longitude:.6f}"
            cv2.putText(img_with_overlay, gps_text,
                        (20, y_offset), font, font_scale, color, thickness)
            y_offset += 20
            acc_text = f"     Accuracy: +/-{self.latest_gps.horizontal_accuracy:.1f}m"
            cv2.putText(img_with_overlay, acc_text,
                        (20, y_offset), font, font_scale, (0, 200, 0), thickness)
            y_offset += 25

        # IMU
        if self.latest_imu:
            accel = self.latest_imu.linear_acceleration
            imu_text = f"IMU: a=[{accel[0]:.3f}, {accel[1]:.3f}, {accel[2]:.3f}]"
            cv2.putText(img_with_overlay, imu_text,
                        (20, y_offset), font, font_scale, (255, 255, 0), thickness)
            y_offset += 25

        # Pose
        if self.latest_pose:
            pos = self.latest_pose.position
            pose_text = f"Pose: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]"
            cv2.putText(img_with_overlay, pose_text,
                        (20, y_offset), font, font_scale, (255, 100, 255), thickness)
            y_offset += 20
            track_text = f"      {self.latest_pose.tracking_state}"
            cv2.putText(img_with_overlay, track_text,
                        (20, y_offset), font, 0.4, (200, 100, 200), thickness)

        return img_with_overlay

    def visualize_loop(self):
        """Main visualization loop (runs in separate thread)"""
        print("📺 Starting visualization windows...")
        print("   Press 'q' in camera window to quit")
        print("   Press 's' to save screenshot")

        cv2.namedWindow('ARVOS Camera Feed', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('ARVOS Camera Feed', 960, 720)

        screenshot_count = 0

        # Try to import Open3D for point cloud visualization
        try:
            import open3d as o3d
            vis = o3d.visualization.Visualizer()
            vis.create_window(window_name='ARVOS LiDAR Point Cloud', width=800, height=600)

            # Create point cloud object
            pcd = o3d.geometry.PointCloud()
            vis.add_geometry(pcd)

            # Set viewpoint
            view_ctl = vis.get_view_control()
            view_ctl.set_zoom(0.5)

            has_open3d = True
            print("✅ Open3D initialized for point cloud visualization")
        except ImportError:
            has_open3d = False
            print("⚠️  Open3D not available - point cloud visualization disabled")
            print("   Install with: pip install open3d")

        while self.running:
            # Display camera feed
            with self.camera_lock:
                if self.latest_camera is not None:
                    display_img = self.create_info_overlay(self.latest_camera)
                    cv2.imshow('ARVOS Camera Feed', display_img)

            # Update point cloud
            if has_open3d:
                with self.depth_lock:
                    if self.latest_depth is not None:
                        try:
                            points = self.latest_depth.point_cloud.points
                            if len(points) > 0:
                                # Convert to numpy array
                                points_array = np.array(points, dtype=np.float64)

                                # Update point cloud
                                pcd.points = o3d.utility.Vector3dVector(points_array)

                                # Color by height (Y coordinate)
                                y_values = points_array[:, 1]
                                y_min, y_max = y_values.min(), y_values.max()
                                if y_max > y_min:
                                    normalized_y = (y_values - y_min) / (y_max - y_min)
                                    colors = np.zeros((len(points), 3))
                                    colors[:, 0] = 1 - normalized_y  # Red for low
                                    colors[:, 1] = normalized_y      # Green for high
                                    pcd.colors = o3d.utility.Vector3dVector(colors)

                                vis.update_geometry(pcd)
                        except Exception as e:
                            print(f"Error updating point cloud: {e}")

                # Update visualization
                vis.poll_events()
                vis.update_renderer()

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quit requested...")
                self.running = False
                break
            elif key == ord('s'):
                # Save screenshot
                with self.camera_lock:
                    if self.latest_camera is not None:
                        screenshot_count += 1
                        filename = f"arvos_screenshot_{screenshot_count}.jpg"
                        cv2.imwrite(filename, self.latest_camera)
                        print(f"📸 Saved screenshot: {filename}")

        # Cleanup
        cv2.destroyAllWindows()
        if has_open3d:
            vis.destroy_window()
        print("Visualization stopped")


def run_server_async(viewer, loop):
    """Run server in the event loop"""
    asyncio.set_event_loop(loop)

    server = MCAPHTTPServer(host="0.0.0.0", port=17500)

    # Set up callbacks
    def on_camera(data):
        viewer.update_camera(data)

    def on_depth(data):
        viewer.update_depth(data)

    def on_gps(data: GPSData):
        viewer.update_gps(data)
        print(f"📍 GPS: {data.latitude:.6f}, {data.longitude:.6f} (±{data.horizontal_accuracy:.1f}m)")

    def on_imu(data: IMUData):
        viewer.update_imu(data)

    def on_pose(data: PoseData):
        viewer.update_pose(data)

    server.on_camera = on_camera
    server.on_depth = on_depth
    server.on_gps = on_gps
    server.on_imu = on_imu
    server.on_pose = on_pose

    # Reconfigure parser callbacks
    server._configure_parser_callbacks()

    print("\n" + "="*60)
    print("🎥 ARVOS Live Viewer")
    print("="*60)
    print("📹 Camera feed will appear in OpenCV window")
    print("🎯 LiDAR point cloud will appear in Open3D window")
    print("📊 Sensor data shown in terminal and overlaid on camera")
    print("\nControls:")
    print("  'q' - Quit")
    print("  's' - Save screenshot")
    print("="*60)
    print()

    try:
        loop.run_until_complete(server.start())
    except KeyboardInterrupt:
        print("\n⏹️  Stopping...")
        viewer.running = False


def main():
    viewer = LiveViewer()

    # Create event loop for server
    loop = asyncio.new_event_loop()

    # Start server in background thread
    server_thread = threading.Thread(
        target=run_server_async,
        args=(viewer, loop),
        daemon=True
    )
    server_thread.start()

    # Give server time to start
    import time
    time.sleep(1)

    # Run visualization in main thread (required for OpenCV/Open3D)
    try:
        viewer.visualize_loop()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping...")
    finally:
        viewer.running = False
        loop.call_soon_threadsafe(loop.stop)


if __name__ == "__main__":
    main()
