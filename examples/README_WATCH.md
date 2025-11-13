# Apple Watch Examples

This directory contains examples for receiving and processing sensor data from Apple Watch connected to iPhone running the Arvos app.

## Prerequisites

1. **iPhone** with Arvos app installed
2. **Apple Watch** (Series 6+) paired with iPhone
3. **Arvos Watch companion app** installed on watch
4. Both devices on same WiFi network as computer

## Setup

### Enable Watch Sensors in Arvos App

1. Open Arvos app on iPhone
2. Go to Settings or Sensor Test view
3. Enable "Apple Watch" toggle
4. Verify watch connection status shows "Connected"

### Run Examples

All examples start a server on port 9090 and display a QR code for easy connection.

## Examples

### 1. Simple Watch Receiver

**File:** `simple_watch_receiver.py`

Minimal example showing basic watch sensor data reception.

```bash
python examples/simple_watch_receiver.py
```

**Receives:**
- Watch IMU data (accelerometer + gyroscope)
- Watch attitude (pitch, roll, yaw)
- Motion activity classification

**Use case:** Quick testing, learning the API

---

### 2. Watch Sensor Viewer

**File:** `watch_sensor_viewer.py`

Full-featured interactive viewer with live statistics and visualization.

```bash
python examples/watch_sensor_viewer.py
```

**Features:**
- Real-time IMU data with magnitude calculations
- Visual acceleration bars
- Attitude visualization with Euler angles
- Motion activity state tracking
- Live FPS and sample rate calculation
- Session statistics

**Use case:** Monitoring watch sensor quality, debugging, demos

---

## Watch Sensor Data Types

### WatchIMUData

High-rate inertial measurement data from Apple Watch.

```python
from arvos.data_types import WatchIMUData

async def on_watch_imu(data: WatchIMUData):
    # Access raw data
    accel_x, accel_y, accel_z = data.linear_acceleration  # m/s²
    gyro_x, gyro_y, gyro_z = data.angular_velocity  # rad/s
    grav_x, grav_y, grav_z = data.gravity  # m/s²

    # Or use numpy arrays
    accel_array = data.linear_acceleration_array
    gyro_array = data.angular_velocity_array
    grav_array = data.gravity_array

    # Timestamp in nanoseconds or seconds
    timestamp_ns = data.timestamp_ns
    timestamp_s = data.timestamp_s
```

**Sample rate:** 50-100 Hz

---

### WatchAttitudeData

Orientation/pose data from Apple Watch motion processing.

```python
from arvos.data_types import WatchAttitudeData
import math

async def on_watch_attitude(data: WatchAttitudeData):
    # Euler angles (radians)
    pitch = data.pitch
    roll = data.roll
    yaw = data.yaw

    # Convert to degrees
    pitch_deg = math.degrees(pitch)

    # Quaternion representation
    qx, qy, qz, qw = data.quaternion
    quat_array = data.quaternion_array  # numpy array

    # Reference frame
    frame = data.reference_frame  # e.g., "XArbitraryZVertical"
```

**Sample rate:** ~50 Hz

---

### WatchMotionActivityData

ML-based classification of user's current activity.

```python
from arvos.data_types import WatchMotionActivityData

async def on_watch_activity(data: WatchMotionActivityData):
    # Activity state
    state = data.state  # "walking", "running", "cycling", "vehicle", "stationary", "unknown"

    # Confidence level (0.0 - 1.0)
    confidence = data.confidence

    if state == "running" and confidence > 0.8:
        print("User is confidently running!")
```

**States:**
- `walking` - User is walking
- `running` - User is running
- `cycling` - User is cycling
- `vehicle` - User is in a vehicle
- `stationary` - User is stationary
- `unknown` - Activity cannot be determined

**Update rate:** When activity changes (typically every few seconds)

---

## Common Patterns

### Logging Watch Data to CSV

```python
import csv
from arvos import ArvosServer

csv_file = open('watch_data.csv', 'w', newline='')
writer = csv.writer(csv_file)
writer.writerow(['timestamp_ns', 'accel_x', 'accel_y', 'accel_z',
                 'gyro_x', 'gyro_y', 'gyro_z'])

async def on_watch_imu(data):
    writer.writerow([
        data.timestamp_ns,
        *data.linear_acceleration,
        *data.angular_velocity
    ])

server = ArvosServer(port=9090)
server.on_watch_imu = on_watch_imu
await server.start()
```

---

### Calculating Watch IMU Statistics

```python
from collections import deque
import numpy as np

# Track last 100 samples
accel_history = deque(maxlen=100)

async def on_watch_imu(data):
    accel = data.linear_acceleration_array
    accel_history.append(accel)

    if len(accel_history) >= 10:
        # Calculate statistics
        all_accel = np.array(list(accel_history))
        mean_accel = np.mean(all_accel, axis=0)
        std_accel = np.std(all_accel, axis=0)

        print(f"Mean accel: {mean_accel}")
        print(f"Std accel: {std_accel}")
```

---

### Detecting Watch Gestures

```python
import numpy as np

async def on_watch_imu(data):
    accel = data.linear_acceleration_array
    gyro = data.angular_velocity_array

    # Calculate magnitudes
    accel_mag = np.linalg.norm(accel)
    gyro_mag = np.linalg.norm(gyro)

    # Detect sharp movements
    if accel_mag > 20.0:  # High acceleration
        print("⚡ Sharp movement detected!")

    # Detect rotation
    if gyro_mag > 5.0:  # High rotation rate
        print("🔄 Rapid rotation detected!")
```

---

### Combining Phone and Watch IMU

```python
from arvos import ArvosServer
from arvos.data_types import IMUData, WatchIMUData

server = ArvosServer(port=9090)

async def on_imu(data: IMUData):
    """Phone IMU"""
    print(f"📱 Phone IMU: {data.linear_acceleration}")

async def on_watch_imu(data: WatchIMUData):
    """Watch IMU"""
    print(f"⌚ Watch IMU: {data.linear_acceleration}")

server.on_imu = on_imu
server.on_watch_imu = on_watch_imu
await server.start()
```

---

## Troubleshooting

### No Watch Data Received

**Problem:** Server starts but no watch sensor data arrives

**Solutions:**
1. Check watch is paired with iPhone (Settings → Bluetooth)
2. Verify watch companion app is installed
3. Enable "Apple Watch" toggle in Arvos app
4. Check watch connection status in Sensor Test view
5. Ensure watch is not in Low Power Mode

---

### Low Sample Rate

**Problem:** Receiving less than 50 Hz from watch

**Solutions:**
1. Close other apps on watch
2. Ensure watch is not in Theater Mode
3. Check iPhone-watch Bluetooth connection
4. Restart both devices if needed

---

### Activity Classification Not Working

**Problem:** Motion activity always shows "unknown"

**Solutions:**
1. Activity detection requires motion - walk around
2. Grant Motion & Fitness permissions to Arvos app
3. Wait a few seconds for classifier to converge
4. Some activities require sustained movement (e.g., running for 10+ seconds)

---

## Advanced Topics

### Timestamp Synchronization

Watch sensor timestamps are synchronized with iPhone system time:

```python
async def on_watch_imu(watch_data):
    watch_time_s = watch_data.timestamp_s

async def on_imu(phone_data):
    phone_time_s = phone_data.timestamp_s

    # Times are directly comparable
    # Both use same nanosecond epoch
```

### Watch Battery Considerations

Watch sensor streaming impacts battery life:

- **IMU @ 50 Hz:** ~5-10% per hour
- **With attitude:** ~7-12% per hour
- **Motion activity only:** <1% per hour

Recommendations:
- Use lower sample rates when possible
- Disable attitude if only IMU is needed
- Monitor watch battery level

---

## Examples from Research Papers

### Gait Analysis

```python
# Track walking cadence from watch IMU
from scipy.signal import find_peaks

accel_history = []

async def on_watch_imu(data):
    accel = data.linear_acceleration_array
    accel_history.append(np.linalg.norm(accel))

    if len(accel_history) >= 200:  # 2 seconds at 100 Hz
        peaks, _ = find_peaks(accel_history[-200:], distance=30)
        cadence = len(peaks) * 30  # steps per minute
        print(f"Cadence: {cadence} steps/min")
```

### Fall Detection

```python
async def on_watch_imu(data):
    accel_mag = np.linalg.norm(data.linear_acceleration_array)

    # Detect freefall (low g-force)
    if accel_mag < 2.0:
        print("⚠️ Possible fall detected!")
```

---

## Further Reading

- [Apple Watch Motion Docs](https://developer.apple.com/documentation/coremotion)
- [Watch Connectivity Guide](https://developer.apple.com/documentation/watchconnectivity)
- Main SDK README: `../README.md`
- Watch Integration (iOS app): `/arvos/WATCH_INTEGRATION.md`
