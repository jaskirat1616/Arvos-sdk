// QR Code generation and connection URL management

function getLocalIP() {
    // Get the current page's hostname
    // In production, this would be replaced with actual IP detection
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') {
        return 'YOUR_COMPUTER_IP';  // Placeholder for local development
    }
    return hostname;
}

function generateConnectionURL() {
    const port = document.getElementById('customPort').value || '8765';
    // Always show placeholder in display text
    const url = `arvos://YOUR_COMPUTER_IP:${port}`;
    return url;
}

function updateQRCode(actualIP) {
    const qrcodeContainer = document.getElementById('qrcode');
    const urlDisplay = document.getElementById('connectionUrl');
    const port = document.getElementById('customPort').value || '8765';

    // QR code gets actual IP if provided, otherwise placeholder
    const qrURL = actualIP ? `arvos://${actualIP}:${port}` : `arvos://YOUR_COMPUTER_IP:${port}`;

    // Display always shows placeholder
    const displayURL = `arvos://YOUR_COMPUTER_IP:${port}`;

    // Clear previous QR code
    qrcodeContainer.innerHTML = '';

    // Check if QRCode library is loaded
    if (typeof QRCode === 'undefined') {
        console.error('QRCode library not loaded');
        qrcodeContainer.innerHTML = '<div style="width:256px;height:256px;display:flex;align-items:center;justify-content:center;background:#f0f0f0;border-radius:8px;"><p style="text-align:center;padding:20px;">QR Code library failed to load.<br>Please check your internet connection.</p></div>';
        urlDisplay.textContent = displayURL;
        urlDisplay.style.color = '#888';
        return;
    }

    // Generate new QR code
    try {
        new QRCode(qrcodeContainer, {
            text: qrURL,  // Actual IP or placeholder
            width: 256,
            height: 256,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });

        urlDisplay.textContent = displayURL;  // Always show placeholder
        urlDisplay.style.color = '#888';
    } catch (error) {
        console.error('Error generating QR code:', error);
        urlDisplay.textContent = 'Error: ' + error.message;
        urlDisplay.style.color = '#ff4444';
    }
}

function goToViewer() {
    const port = document.getElementById('customPort').value || '8765';
    window.location.href = `viewer.html?port=${port}`;
}

function detectLocalIP() {
    // Detect actual IP for QR code, but show placeholder in text
    const RTCPeerConnection = window.RTCPeerConnection ||
                               window.webkitRTCPeerConnection ||
                               window.mozRTCPeerConnection;

    if (!RTCPeerConnection) {
        updateQRCode();
        return;
    }

    const pc = new RTCPeerConnection({iceServers: []});
    pc.createDataChannel('');

    pc.createOffer().then(offer => pc.setLocalDescription(offer));

    pc.onicecandidate = (ice) => {
        if (!ice || !ice.candidate || !ice.candidate.candidate) {
            pc.close();
            return;
        }

        const candidate = ice.candidate.candidate;
        const ipRegex = /([0-9]{1,3}\.){3}[0-9]{1,3}/;
        const match = ipRegex.exec(candidate);

        if (match) {
            const detectedIP = match[0];
            console.log('Detected IP:', detectedIP);

            // Update QR code with actual IP
            updateQRCode(detectedIP);
            pc.close();
        }
    };
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    // Try to detect IP first
    detectLocalIP();

    // Fallback to placeholder after 2 seconds if detection fails
    setTimeout(() => {
        const urlDisplay = document.getElementById('connectionUrl');
        if (urlDisplay.textContent === 'Generating QR code...') {
            updateQRCode(null);  // No IP detected, use placeholder
        }
    }, 2000);
});
