// Three.js Point Cloud Viewer for ARVOS

let scene, camera, renderer, controls;
let pointCloud = null;
let poseTrail = null;
let maxPoints = 100000; // Max points to render
let currentPoints = [];
let poseHistory = [];
let maxPoseHistory = 1000;

function initViewer() {
    const container = document.getElementById('canvas-container');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    scene.fog = new THREE.Fog(0x1a1a1a, 10, 50);

    // Camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(75, aspect, 0.01, 1000);
    camera.position.set(0, 2, 5);
    camera.lookAt(0, 0, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 0.1;
    controls.maxDistance = 100;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Grid
    const gridHelper = new THREE.GridHelper(10, 20, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Axes
    const axesHelper = new THREE.AxesHelper(1);
    scene.add(axesHelper);

    // Create point cloud geometry
    createPointCloudObject();

    // Create pose trail
    createPoseTrail();

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Start render loop
    animate();

    console.log('Three.js viewer initialized');
}

function createPointCloudObject() {
    const geometry = new THREE.BufferGeometry();

    // Pre-allocate buffers
    const positions = new Float32Array(maxPoints * 3);
    const colors = new Float32Array(maxPoints * 3);

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 0.02,
        vertexColors: true,
        sizeAttenuation: true
    });

    pointCloud = new THREE.Points(geometry, material);
    pointCloud.frustumCulled = false;
    scene.add(pointCloud);
}

function createPoseTrail() {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(maxPoseHistory * 3);
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.LineBasicMaterial({
        color: 0xff6b35,
        linewidth: 2
    });

    poseTrail = new THREE.Line(geometry, material);
    scene.add(poseTrail);
}

function updatePointCloud(points) {
    if (!pointCloud || !points || points.length === 0) return;

    currentPoints = points;

    const geometry = pointCloud.geometry;
    const positions = geometry.attributes.position.array;
    const colors = geometry.attributes.color.array;

    const numPoints = Math.min(points.length, maxPoints);

    for (let i = 0; i < numPoints; i++) {
        const point = points[i];

        // Position
        positions[i * 3] = point.x;
        positions[i * 3 + 1] = point.y;
        positions[i * 3 + 2] = point.z;

        // Color (from depth or RGB)
        if (point.r !== undefined) {
            colors[i * 3] = point.r / 255;
            colors[i * 3 + 1] = point.g / 255;
            colors[i * 3 + 2] = point.b / 255;
        } else {
            // Color by depth
            const depth = Math.sqrt(point.x * point.x + point.y * point.y + point.z * point.z);
            const color = depthToColor(depth);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }
    }

    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.color.needsUpdate = true;
    geometry.setDrawRange(0, numPoints);
}

function updatePoseVisualization(poseMessage) {
    if (!poseMessage || !poseMessage.position) return;

    const pos = poseMessage.position;

    // Add to pose history
    poseHistory.push({ x: pos.x, y: pos.y, z: pos.z });
    if (poseHistory.length > maxPoseHistory) {
        poseHistory.shift();
    }

    // Update trail
    const positions = poseTrail.geometry.attributes.position.array;
    for (let i = 0; i < poseHistory.length; i++) {
        positions[i * 3] = poseHistory[i].x;
        positions[i * 3 + 1] = poseHistory[i].y;
        positions[i * 3 + 2] = poseHistory[i].z;
    }

    poseTrail.geometry.attributes.position.needsUpdate = true;
    poseTrail.geometry.setDrawRange(0, poseHistory.length);
}

function depthToColor(depth) {
    // Map depth (0-5m) to color gradient (blue -> cyan -> green -> yellow -> red)
    const normalized = Math.min(depth / 5.0, 1.0);

    if (normalized < 0.25) {
        // Blue to Cyan
        const t = normalized / 0.25;
        return { r: 0, g: t, b: 1 };
    } else if (normalized < 0.5) {
        // Cyan to Green
        const t = (normalized - 0.25) / 0.25;
        return { r: 0, g: 1, b: 1 - t };
    } else if (normalized < 0.75) {
        // Green to Yellow
        const t = (normalized - 0.5) / 0.25;
        return { r: t, g: 1, b: 0 };
    } else {
        // Yellow to Red
        const t = (normalized - 0.75) / 0.25;
        return { r: 1, g: 1 - t, b: 0 };
    }
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// UI Control functions
function togglePointCloud() {
    if (pointCloud) {
        pointCloud.visible = !pointCloud.visible;
    }
}

function toggleCamera() {
    // Toggle camera overlay (implemented in camera-view.js)
    if (window.toggleCameraOverlay) {
        window.toggleCameraOverlay();
    }
}

function resetView() {
    camera.position.set(0, 2, 5);
    camera.lookAt(0, 0, 0);
    controls.reset();
}

// Export function for PLY format
window.exportPointCloudPLY = function() {
    if (!currentPoints || currentPoints.length === 0) {
        console.warn('No point cloud data to export');
        return null;
    }

    let ply = 'ply\n';
    ply += 'format ascii 1.0\n';
    ply += `element vertex ${currentPoints.length}\n`;
    ply += 'property float x\n';
    ply += 'property float y\n';
    ply += 'property float z\n';
    ply += 'property uchar red\n';
    ply += 'property uchar green\n';
    ply += 'property uchar blue\n';
    ply += 'end_header\n';

    currentPoints.forEach(point => {
        const r = point.r !== undefined ? point.r : 128;
        const g = point.g !== undefined ? point.g : 128;
        const b = point.b !== undefined ? point.b : 128;
        ply += `${point.x} ${point.y} ${point.z} ${r} ${g} ${b}\n`;
    });

    return ply;
};

// Export function for frame capture
window.captureCurrentFrame = function() {
    renderer.render(scene, camera);
    return renderer.domElement.toDataURL('image/png');
};

// Binary point cloud parser
function parsePointCloudBinary(arrayBuffer, pointCount) {
    const dataStart = 32; // Skip header
    const view = new DataView(arrayBuffer);
    const points = [];

    for (let i = 0; i < pointCount; i++) {
        const offset = dataStart + (i * 16); // 4 floats per point (x, y, z, confidence)

        const x = view.getFloat32(offset, true);
        const y = view.getFloat32(offset + 4, true);
        const z = view.getFloat32(offset + 8, true);
        const confidence = view.getFloat32(offset + 12, true);

        if (confidence > 0.5) { // Filter low-confidence points
            points.push({ x, y, z });
        }
    }

    updatePointCloud(points);
}
