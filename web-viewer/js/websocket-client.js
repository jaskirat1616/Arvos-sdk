// ARVOS WebSocket Client
// Handles connection and message parsing from ARVOS iOS app

let ws = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectDelay = 2000;
let lastMessageTime = 0;
let messageCount = 0;
let fpsCounter = 0;
let fpsInterval = null;

// Message handlers
const messageHandlers = {
    camera: handleCameraFrame,
    depth: handleDepthFrame,
    imu: handleIMUData,
    pose: handlePoseData,
    gps: handleGPSData
};

function connectToARVOS(port) {
    const host = window.location.hostname || 'localhost';
    const wsURL = `ws://${host}:${port}`;

    updateStatus('connecting', 'Connecting...');
    document.getElementById('connHost').textContent = host;

    try {
        ws = new WebSocket(wsURL);
        ws.binaryType = 'arraybuffer';

        ws.onopen = () => {
            console.log('Connected to ARVOS');
            updateStatus('connected', 'Connected');
            reconnectAttempts = 0;
            startFPSCounter();
        };

        ws.onmessage = (event) => {
            handleMessage(event.data);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('disconnected', 'Connection Error');
        };

        ws.onclose = () => {
            console.log('Disconnected from ARVOS');
            updateStatus('disconnected', 'Disconnected');
            stopFPSCounter();
            attemptReconnect(port);
        };

    } catch (error) {
        console.error('Failed to connect:', error);
        updateStatus('disconnected', 'Failed to Connect');
    }
}

function handleMessage(data) {
    try {
        // Check if binary or JSON
        if (typeof data === 'string') {
            const message = JSON.parse(data);
            routeMessage(message);
        } else {
            // Binary data (e.g., compressed point cloud)
            handleBinaryMessage(data);
        }

        // Update stats
        messageCount++;
        fpsCounter++;
        lastMessageTime = Date.now();

    } catch (error) {
        console.error('Error handling message:', error);
    }
}

function routeMessage(message) {
    const messageType = message.type;

    if (messageHandlers[messageType]) {
        messageHandlers[messageType](message);
    } else {
        console.log('Unknown message type:', messageType, message);
    }
}

function handleBinaryMessage(arrayBuffer) {
    // Handle binary point cloud data
    // Format: [header (32 bytes)][point data]
    const view = new DataView(arrayBuffer);

    // Read header
    const magic = view.getUint32(0, true); // Should be 0x41525653 ('ARVS')
    const version = view.getUint16(4, true);
    const dataType = view.getUint16(6, true); // 1=depth, 2=camera, etc.
    const pointCount = view.getUint32(8, true);

    if (magic !== 0x41525653) {
        console.warn('Invalid binary message header');
        return;
    }

    if (dataType === 1) {
        // Depth/Point cloud data
        parsePointCloudBinary(arrayBuffer, pointCount);
    }
}

function handleCameraFrame(message) {
    // Camera frame as base64 JPEG or binary
    if (message.image) {
        updateCameraView(message.image);
    }

    if (message.intrinsics) {
        // Camera intrinsics for 3D reconstruction
        updateCameraIntrinsics(message.intrinsics);
    }
}

function handleDepthFrame(message) {
    // Depth data as point cloud or depth map
    if (message.points) {
        updatePointCloud(message.points);
        document.getElementById('statsPoints').textContent = message.points.length;
    }

    if (message.confidence) {
        // Depth confidence map (research feature)
        console.log('Depth confidence:', message.confidence);
    }
}

function handleIMUData(message) {
    const imuText = `a:${formatVector(message.acceleration)} g:${formatVector(message.rotation)}`;
    document.getElementById('imuData').textContent = imuText;

    if (message.calibration) {
        // IMU calibration data (research feature)
        console.log('IMU calibration:', message.calibration);
    }
}

function handlePoseData(message) {
    const pos = message.position || {x:0, y:0, z:0};
    const poseText = `(${pos.x.toFixed(2)}, ${pos.y.toFixed(2)}, ${pos.z.toFixed(2)})`;
    document.getElementById('poseData').textContent = poseText;

    // Update 3D visualization
    if (window.updatePoseVisualization) {
        updatePoseVisualization(message);
    }

    if (message.trackingState) {
        // Pose validity flag (research feature)
        console.log('Tracking state:', message.trackingState);
    }
}

function handleGPSData(message) {
    if (message.latitude && message.longitude) {
        const gpsText = `${message.latitude.toFixed(6)}, ${message.longitude.toFixed(6)}`;
        document.getElementById('gpsData').textContent = gpsText;
    }
}

function updateStatus(state, text) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const connStatus = document.getElementById('connStatus');

    indicator.className = 'status-indicator ' + state;
    statusText.textContent = text;
    connStatus.textContent = text;
}

function attemptReconnect(port) {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.log('Max reconnection attempts reached');
        updateStatus('disconnected', 'Connection Failed');
        return;
    }

    reconnectAttempts++;
    const delay = reconnectDelay * Math.pow(1.5, reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);

    setTimeout(() => {
        connectToARVOS(port);
    }, delay);
}

function startFPSCounter() {
    fpsCounter = 0;
    fpsInterval = setInterval(() => {
        document.getElementById('statsFPS').textContent = fpsCounter;
        fpsCounter = 0;

        // Update latency
        const latency = Date.now() - lastMessageTime;
        document.getElementById('statsLatency').textContent = latency + 'ms';
    }, 1000);
}

function stopFPSCounter() {
    if (fpsInterval) {
        clearInterval(fpsInterval);
        fpsInterval = null;
    }
    document.getElementById('statsFPS').textContent = '0';
}

// Utility functions
function formatVector(vec) {
    if (!vec) return '-';
    return `(${vec.x.toFixed(2)}, ${vec.y.toFixed(2)}, ${vec.z.toFixed(2)})`;
}

// Export functions
function downloadPointCloud() {
    if (window.exportPointCloudPLY) {
        const plyData = window.exportPointCloudPLY();
        if (plyData) {
            downloadFile(plyData, 'arvos_pointcloud.ply', 'text/plain');
        }
    }
}

function captureFrame() {
    if (window.captureCurrentFrame) {
        const imageData = window.captureCurrentFrame();
        if (imageData) {
            downloadFile(imageData, 'arvos_frame.png', 'image/png');
        }
    }
}

function downloadFile(data, filename, mimeType) {
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Send message to ARVOS (for control commands)
function sendCommand(command) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(command));
    }
}
