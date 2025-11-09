# Arvos 3D Visualization

## Overview

The live camera view now includes three separate windows with optimized performance:

1. **Camera Feed Window** - Live RGB camera stream with sensor overlay
2. **3D Point Cloud Window** - Interactive 3D LiDAR/depth visualization (Open3D)
3. **GPS Map Window** - Real-time GPS location on OpenStreetMap

## Installation

Install required dependencies:

```bash
pip install opencv-python Pillow numpy requests open3d
```

## Usage

```bash
python live_camera_view.py
```

## Features

### 1. Camera Feed (30 FPS)
- High-quality RGB video stream from iPhone
- Real-time sensor data overlay (IMU, Pose, GPS, Depth stats)
- Optimized for smooth playback

### 2. 3D Point Cloud (Interactive)
- **Interactive 3D visualization** using Open3D
- Rotate, zoom, and pan with mouse
- Color-coded depth (blue = close, red = far)
- Real-time updates from LiDAR sensor
- Similar to Foxglove's 3D panel

**Mouse Controls:**
- Left click + drag: Rotate view
- Right click + drag: Pan view
- Scroll wheel: Zoom in/out

### 3. GPS Map
- OpenStreetMap tiles at street level
- Position marker with accuracy circle
- Cached for performance (only updates when moved >10m)
- Live GPS coordinates overlay

## Performance Optimizations

### Camera FPS Fix
- Reduced async sleep to 1ms for faster frame processing
- Depth and GPS windows update less frequently to prevent blocking:
  - Depth: Updates every 5 frames
  - GPS: Updates every 30 frames (maps change slowly)

### PLY Parsing Fix
- Added buffer size validation to prevent crashes
- Handles malformed PLY data gracefully
- Filters NaN and infinite values

### Display Loop Optimization
- Non-blocking Open3D visualization
- GPS map caching prevents redundant downloads
- Efficient frame processing pipeline

## Troubleshooting

### Low Camera FPS
- Make sure your iPhone is on the same Wi-Fi network
- Check that no other apps are using the camera
- Reduce depth update frequency if needed

### Point Cloud Not Showing
- Ensure your iPhone has LiDAR (iPhone 12 Pro and newer)
- Check that depth is enabled in streaming mode
- Open3D window may take a few seconds to initialize

### GPS Map Not Loading
- Check internet connection
- OpenStreetMap may rate-limit requests
- Map is cached, so it will reuse previous tile if download fails

## Technical Details

### Data Flow
1. iPhone captures sensor data (camera, LiDAR, IMU, GPS)
2. Data is compressed and sent via WebSocket
3. Python SDK receives and decodes data
4. Three separate visualization windows display data in real-time

### Point Cloud Format
- Binary PLY format (little-endian)
- XYZ positions (float32) + RGB colors (uint8)
- Filtered for valid depth range and finite values

### GPS Map Tiles
- OpenStreetMap tile API (zoom level 17)
- Composite multi-tile image for coverage
- Meter-to-pixel accuracy calculation
