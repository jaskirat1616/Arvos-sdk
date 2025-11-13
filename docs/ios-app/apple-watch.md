# Apple Watch Integration

Stream wearable sensor data from your Apple Watch alongside iPhone sensors.

## Overview

The ARVOS app supports Apple Watch as a companion device, streaming wearable IMU, attitude, and motion activity data in sync with iPhone sensors.

## Requirements

### Apple Watch
- Apple Watch Series 6 or newer
- watchOS 9.0+
- Paired with streaming iPhone

### iPhone
- Same requirements as main app
- Watch app installed (installs automatically)

## Setup

### Step 1: Build iOS App

The Watch app is included in the iOS app project:
1. Open Xcode project
2. Build for iPhone
3. Watch app installs automatically on paired watch

### Step 2: Enable Watch in App

1. Open ARVOS app on iPhone
2. Go to **Settings**
3. Find **"Apple Watch"** section
4. Toggle **"Enable Watch Streaming"**

### Step 3: Verify Connection

1. Check connection indicator (should show green)
2. Open **Sensor Test** view
3. Toggle **"Apple Watch"** on
4. Watch data should appear

## Watch Sensors

### IMU Data
- **Rate**: 50-100 Hz
- **Sensors**: Accelerometer, gyroscope, gravity
- **Synchronization**: Nanosecond timestamps
- **Format**: Same as iPhone IMU

### Attitude Data
- **Quaternion**: x, y, z, w
- **Euler Angles**: Pitch, roll, yaw
- **Reference Frame**: Configurable
- **Rate**: 50-100 Hz

### Motion Activity
- **States**: Walking, running, cycling, vehicle, stationary, unknown
- **Confidence**: 0.0 - 1.0
- **Updates**: Real-time classification

## Usage

### Enable in Streaming

1. Start streaming session
2. Watch data automatically included
3. Data flows through same protocol as iPhone data
4. Tagged with `sensorType: "watch_imu"`, etc.

### View in Sensor Test

1. Open **Sensor Test** view
2. Toggle **"Apple Watch"** section
3. View real-time watch data
4. Monitor sample rates

### Recording

Watch data is automatically included in MCAP recordings:
- Same timestamp synchronization
- Same file format
- All watch sensors preserved

## Data Format

### Watch IMU

```json
{
  "sensorType": "watch_imu",
  "timestampNs": 186832704657666,
  "angularVelocity": [0.01, -0.02, 0.005],
  "linearAcceleration": [0.1, 0.0, -0.01],
  "gravity": [0.0, 0.0, -9.81]
}
```

### Watch Attitude

```json
{
  "sensorType": "watch_attitude",
  "timestampNs": 186832704657666,
  "quaternion": [0.0, 0.0, 0.0, 1.0],
  "pitch": 0.0,
  "roll": 0.0,
  "yaw": 0.0,
  "referenceFrame": "xArbitraryZVertical"
}
```

### Watch Activity

```json
{
  "sensorType": "watch_activity",
  "timestampNs": 186832704657666,
  "state": "walking",
  "confidence": 0.95
}
```

## Synchronization

Watch data is synchronized with iPhone sensors:
- **Nanosecond timestamps** - Precise synchronization
- **Same protocol** - Flows through same connection
- **Same format** - Consistent data structure

## Use Cases

### Robotics Operators
- Track operator hand/arm motion
- Human-in-the-loop research
- Telepresence applications

### Motion Analysis
- Gait analysis
- Activity recognition
- Biomechanics research

### Sensor Fusion
- Combine iPhone + Watch IMU
- Multi-device sensor fusion
- Redundant sensor systems

## Troubleshooting

### Watch Not Connecting

- Ensure watch is paired with iPhone
- Check Bluetooth is enabled
- Verify watch app is installed
- Restart both devices

### No Watch Data

- Check "Enable Watch Streaming" is on
- Verify watch is nearby (Bluetooth range)
- Check watch app is running
- Review connection indicator

### Low Sample Rate

- Check watch battery level
- Ensure watch is on wrist (motion detection)
- Verify watchOS version (9.0+)
- Check Bluetooth signal strength

## Next Steps

- [Watch Examples](../examples/apple-watch.md) - Python examples
- [Usage Guide](usage.md) - Complete app guide
- [Troubleshooting](../guides/troubleshooting.md) - Common issues

