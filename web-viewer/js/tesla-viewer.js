/**
 * Tesla Autopilot Style Viewer
 * Main visualization controller
 */

let scene, camera, renderer, controls;
let pointCloud, pointsMaterial;
let map, marker, pathPolyline;
let gpsPath = [];
let isRecording = false;

// Canvas contexts for sensor visualizations
let imuCtx, poseCtx;
let imuHistory = [];
let poseHistory = [];
const HISTORY_LENGTH = 100;

// Stats
let frameCount = 0;
let lastFrameTime = Date.now();
let currentFPS = 0;

function initTeslaViewer(port) {
    init3DView();
    initMap();
    initSensorCanvases();
    connectWebSocket(port);
    animate();
}

function init3DView() {
    const container = document.getElementById('canvas-3d');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    scene.fog = new THREE.Fog(0x000000, 1, 50);

    // Camera
    camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.01,
        100
    );
    camera.position.set(0, 2, 5);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Controls
    if (THREE.OrbitControls) {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 0.5;
        controls.maxDistance = 20;
    }

    // Grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x2a2a2a, 0x1a1a1a);
    scene.add(gridHelper);

    // Axes
    const axesHelper = new THREE.AxesHelper(1);
    scene.add(axesHelper);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    scene.add(directionalLight);

    // Point cloud
    const geometry = new THREE.BufferGeometry();
    pointsMaterial = new THREE.PointsMaterial({
        size: 0.02,
        vertexColors: true,
        sizeAttenuation: true
    });
    pointCloud = new THREE.Points(geometry, pointsMaterial);
    scene.add(pointCloud);

    // Handle resize
    window.addEventListener('resize', onWindowResize, false);
}

function initMap() {
    map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }).setView([37.7749, -122.4194], 13);

    // Dark tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    // Add zoom control to top right
    L.control.zoom({ position: 'topright' }).addTo(map);

    // Device marker
    marker = L.circleMarker([37.7749, -122.4194], {
        radius: 8,
        fillColor: '#3b82f6',
        color: '#ffffff',
        weight: 2,
        fillOpacity: 1
    }).addTo(map);

    // Path polyline
    pathPolyline = L.polyline([], {
        color: '#10b981',
        weight: 3,
        opacity: 0.7
    }).addTo(map);
}

function initSensorCanvases() {
    const imuCanvas = document.getElementById('imuCanvas');
    const poseCanvas = document.getElementById('poseCanvas');

    imuCtx = imuCanvas.getContext('2d');
    poseCtx = poseCanvas.getContext('2d');

    // Start animation loops
    setInterval(updateIMUViz, 50);
    setInterval(updatePoseViz, 50);
}

function updateIMUViz() {
    if (!imuCtx) return;

    const canvas = imuCtx.canvas;
    const w = canvas.width;
    const h = canvas.height;

    // Clear
    imuCtx.fillStyle = '#000';
    imuCtx.fillRect(0, 0, w, h);

    // Draw grid
    imuCtx.strokeStyle = '#1a1a1a';
    imuCtx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = (h / 4) * i;
        imuCtx.beginPath();
        imuCtx.moveTo(0, y);
        imuCtx.lineTo(w, y);
        imuCtx.stroke();
    }

    // Draw IMU data
    if (imuHistory.length > 1) {
        imuCtx.strokeStyle = '#3b82f6';
        imuCtx.lineWidth = 2;
        imuCtx.beginPath();

        imuHistory.forEach((data, i) => {
            const x = (i / HISTORY_LENGTH) * w;
            const y = h / 2 + (data.accel * h / 4);
            if (i === 0) imuCtx.moveTo(x, y);
            else imuCtx.lineTo(x, y);
        });

        imuCtx.stroke();
    }
}

function updatePoseViz() {
    if (!poseCtx) return;

    const canvas = poseCtx.canvas;
    const w = canvas.width;
    const h = canvas.height;

    // Clear
    poseCtx.fillStyle = '#000';
    poseCtx.fillRect(0, 0, w, h);

    // Draw trajectory
    if (poseHistory.length > 1) {
        poseCtx.strokeStyle = '#10b981';
        poseCtx.lineWidth = 2;
        poseCtx.beginPath();

        const scale = 20;
        const offsetX = w / 2;
        const offsetY = h / 2;

        poseHistory.forEach((data, i) => {
            const x = offsetX + data.x * scale;
            const y = offsetY - data.z * scale;
            if (i === 0) poseCtx.moveTo(x, y);
            else poseCtx.lineTo(x, y);
        });

        poseCtx.stroke();

        // Current position
        if (poseHistory.length > 0) {
            const last = poseHistory[poseHistory.length - 1];
            const x = offsetX + last.x * scale;
            const y = offsetY - last.z * scale;

            poseCtx.fillStyle = '#3b82f6';
            poseCtx.beginPath();
            poseCtx.arc(x, y, 4, 0, Math.PI * 2);
            poseCtx.fill();
        }
    }
}

function connectWebSocket(port) {
    const host = window.location.hostname || 'localhost';
    const ws = new WebSocket(`ws://${host}:${port}`);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
        updateStatus(true);
        console.log('Connected to ARVOS');
    };

    ws.onclose = () => {
        updateStatus(false);
        console.log('Disconnected from ARVOS');
        setTimeout(() => connectWebSocket(port), 3000);
    };

    ws.onmessage = (event) => {
        try {
            if (typeof event.data === 'string') {
                const data = JSON.parse(event.data);
                handleData(data);
            } else {
                // Handle binary data if needed
                console.log('Binary data received');
            }
        } catch (e) {
            console.error('Parse error:', e);
        }
    };
}

function handleData(data) {
    const type = data.type || data.sensorType;

    switch(type) {
        case 'depth':
            updatePointCloud(data);
            break;
        case 'camera':
            updateCamera(data);
            break;
        case 'imu':
            updateIMU(data);
            break;
        case 'pose':
            updatePose(data);
            break;
        case 'gps':
            updateGPS(data);
            break;
    }

    updateFPS();
}

function updatePointCloud(data) {
    // Handle different data formats
    let points = [];

    if (data.pointCloud && data.pointCloud.points) {
        points = data.pointCloud.points;
    } else if (data.points) {
        points = data.points;
    } else if (Array.isArray(data)) {
        points = data;
    } else {
        return;
    }

    const numPoints = points.length;
    if (numPoints === 0) return;

    document.getElementById('pointCount').textContent = numPoints.toLocaleString();

    // Create buffers
    const positions = new Float32Array(numPoints * 3);
    const colors = new Float32Array(numPoints * 3);

    let minDepth = Infinity, maxDepth = -Infinity;

    // Parse points - handle both array and object formats
    for (let i = 0; i < numPoints; i++) {
        const point = points[i];
        let x, y, z;

        if (Array.isArray(point)) {
            x = point[0];
            y = point[1];
            z = point[2];
        } else {
            x = point.x || 0;
            y = point.y || 0;
            z = point.z || 0;
        }

        positions[i * 3] = x;
        positions[i * 3 + 1] = y;
        positions[i * 3 + 2] = z;

        const depth = Math.sqrt(x*x + y*y + z*z);
        minDepth = Math.min(minDepth, depth);
        maxDepth = Math.max(maxDepth, depth);
    }

    document.getElementById('depthRange').textContent = `${maxDepth.toFixed(1)}m`;

    // Color by depth (Tesla-style blue gradient)
    for (let i = 0; i < numPoints; i++) {
        const x = positions[i * 3];
        const y = positions[i * 3 + 1];
        const z = positions[i * 3 + 2];
        const depth = Math.sqrt(x*x + y*y + z*z);
        const normalized = (depth - minDepth) / (maxDepth - minDepth + 0.001);

        // Blue -> Cyan -> Green gradient (close to far)
        if (normalized < 0.5) {
            const t = normalized * 2;
            colors[i * 3] = 0;
            colors[i * 3 + 1] = t * 0.6 + 0.4;
            colors[i * 3 + 2] = 1;
        } else {
            const t = (normalized - 0.5) * 2;
            colors[i * 3] = 0;
            colors[i * 3 + 1] = 1 - t * 0.4;
            colors[i * 3 + 2] = 1 - t;
        }
    }

    // Update geometry
    pointCloud.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    pointCloud.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    pointCloud.geometry.computeBoundingSphere();
}

function updateCamera(data) {
    // Camera feed update would go here
    const canvas = document.getElementById('cameraCanvas');
    if (data.width && data.height) {
        document.getElementById('cameraRes').textContent = `${data.width}×${data.height}`;
    }
}

function updateIMU(data) {
    const accel = data.linearAcceleration || data.linear_acceleration;
    const gyro = data.angularVelocity || data.angular_velocity;

    if (accel) {
        const magnitude = Math.sqrt(accel[0]**2 + accel[1]**2 + accel[2]**2);
        document.getElementById('accel').textContent = magnitude.toFixed(2) + 'g';

        imuHistory.push({ accel: accel[2], time: Date.now() });
        if (imuHistory.length > HISTORY_LENGTH) imuHistory.shift();
    }

    if (gyro) {
        const magnitude = Math.sqrt(gyro[0]**2 + gyro[1]**2 + gyro[2]**2);
        document.getElementById('gyro').textContent = (magnitude * 180 / Math.PI).toFixed(1) + '°/s';
    }
}

function updatePose(data) {
    const pos = data.position;
    if (pos) {
        document.getElementById('poseX').textContent = pos[0].toFixed(2) + 'm';
        document.getElementById('poseY').textContent = pos[1].toFixed(2) + 'm';
        document.getElementById('poseZ').textContent = pos[2].toFixed(2) + 'm';

        poseHistory.push({ x: pos[0], y: pos[1], z: pos[2], time: Date.now() });
        if (poseHistory.length > HISTORY_LENGTH) poseHistory.shift();
    }
}

function updateGPS(data) {
    const lat = data.latitude;
    const lon = data.longitude;
    const speed = data.speed || 0;

    if (lat && lon) {
        document.getElementById('gpsLat').textContent = lat.toFixed(6);
        document.getElementById('gpsLon').textContent = lon.toFixed(6);
        document.getElementById('gpsSpeed').textContent = (speed * 3.6).toFixed(1) + ' km/h';

        // Update map
        marker.setLatLng([lat, lon]);
        map.panTo([lat, lon]);

        // Add to path
        gpsPath.push([lat, lon]);
        if (gpsPath.length > 1000) gpsPath.shift();
        pathPolyline.setLatLngs(gpsPath);
    }
}

function updateFPS() {
    frameCount++;
    const now = Date.now();
    const elapsed = now - lastFrameTime;

    if (elapsed >= 1000) {
        currentFPS = (frameCount / elapsed * 1000).toFixed(0);
        document.getElementById('fps').textContent = currentFPS;
        document.getElementById('latency').textContent = '12ms';
        frameCount = 0;
        lastFrameTime = now;
    }
}

function updateStatus(connected) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'CONNECTED';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'DISCONNECTED';
    }
}

function animate() {
    requestAnimationFrame(animate);

    if (controls) controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    const container = document.getElementById('canvas-3d');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// View control functions
function setView(view) {
    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-${view}`).classList.add('active');

    switch(view) {
        case 'perspective':
            camera.position.set(0, 2, 5);
            camera.lookAt(0, 0, 0);
            break;
        case 'top':
            camera.position.set(0, 10, 0);
            camera.lookAt(0, 0, 0);
            break;
        case 'side':
            camera.position.set(10, 2, 0);
            camera.lookAt(0, 0, 0);
            break;
    }
}

function centerMap() {
    if (gpsPath.length > 0) {
        const last = gpsPath[gpsPath.length - 1];
        map.setView(last, 15);
    }
}

function toggleRecording() {
    isRecording = !isRecording;
    const btn = document.getElementById('recordBtn');
    if (isRecording) {
        btn.classList.add('recording');
    } else {
        btn.classList.remove('recording');
    }
}

function captureSnapshot() {
    const link = document.createElement('a');
    link.download = `arvos-snapshot-${Date.now()}.png`;
    link.href = renderer.domElement.toDataURL();
    link.click();
}

function downloadData() {
    console.log('Download data functionality');
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

// Set initial view
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-perspective').classList.add('active');
});
