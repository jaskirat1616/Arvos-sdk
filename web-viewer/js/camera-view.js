// Camera Feed Overlay for ARVOS Viewer

let cameraOverlay = null;
let cameraImage = null;
let cameraIntrinsics = null;
let isOverlayVisible = false;

function initCameraOverlay() {
    // Create overlay canvas/div if it doesn't exist
    if (!cameraOverlay) {
        cameraOverlay = document.createElement('div');
        cameraOverlay.id = 'camera-overlay';
        cameraOverlay.style.cssText = `
            position: absolute;
            top: 20px;
            left: 20px;
            width: 320px;
            height: 240px;
            border: 2px solid #FF6B35;
            border-radius: 8px;
            overflow: hidden;
            background: #000;
            display: none;
        `;

        cameraImage = document.createElement('img');
        cameraImage.style.cssText = `
            width: 100%;
            height: 100%;
            object-fit: contain;
        `;

        cameraOverlay.appendChild(cameraImage);
        document.getElementById('canvas-container').appendChild(cameraOverlay);
    }
}

function updateCameraView(imageData) {
    if (!cameraOverlay) {
        initCameraOverlay();
    }

    // imageData can be base64 or blob URL
    if (typeof imageData === 'string') {
        if (!imageData.startsWith('data:')) {
            // Assume base64 JPEG
            cameraImage.src = 'data:image/jpeg;base64,' + imageData;
        } else {
            cameraImage.src = imageData;
        }
    }
}

function updateCameraIntrinsics(intrinsics) {
    cameraIntrinsics = intrinsics;
    // Store for potential 3D projection use
    console.log('Camera intrinsics updated:', intrinsics);
}

window.toggleCameraOverlay = function() {
    if (!cameraOverlay) {
        initCameraOverlay();
    }

    isOverlayVisible = !isOverlayVisible;
    cameraOverlay.style.display = isOverlayVisible ? 'block' : 'none';
};

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCameraOverlay);
} else {
    initCameraOverlay();
}
