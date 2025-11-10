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

function updateQRCode() {
    const qrcodeContainer = document.getElementById('qrcode');
    const urlDisplay = document.getElementById('connectionUrl');
    const connectionURL = generateConnectionURL();

    // Clear previous QR code
    qrcodeContainer.innerHTML = '';

    // Check if QRCode library is loaded
    if (typeof QRCode === 'undefined') {
        console.error('QRCode library not loaded');
        qrcodeContainer.innerHTML = '<div style="width:256px;height:256px;display:flex;align-items:center;justify-content:center;background:#f0f0f0;border-radius:8px;"><p style="text-align:center;padding:20px;">QR Code library failed to load.<br>Please check your internet connection.</p></div>';
        urlDisplay.textContent = connectionURL;
        urlDisplay.style.color = '#666';
        return;
    }

    // Generate new QR code
    try {
        new QRCode(qrcodeContainer, {
            text: connectionURL,
            width: 256,
            height: 256,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });

        urlDisplay.textContent = connectionURL;
        urlDisplay.style.color = '#666';
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
            const port = document.getElementById('customPort').value || '8765';

            // QR code uses actual IP
            const qrURL = `arvos://${detectedIP}:${port}`;

            // Display shows placeholder
            const displayURL = `arvos://YOUR_COMPUTER_IP:${port}`;

            const qrcodeContainer = document.getElementById('qrcode');
            const urlDisplay = document.getElementById('connectionUrl');

            // Clear and regenerate QR with actual IP
            qrcodeContainer.innerHTML = '';

            if (typeof QRCode !== 'undefined') {
                new QRCode(qrcodeContainer, {
                    text: qrURL,  // Actual IP in QR code
                    width: 256,
                    height: 256,
                    colorDark: '#000000',
                    colorLight: '#ffffff',
                    correctLevel: QRCode.CorrectLevel.M
                });
            }

            // Show placeholder text to user
            urlDisplay.textContent = displayURL;
            urlDisplay.style.color = '#888';
            pc.close();
        }
    };
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    // Try to detect IP first
    detectLocalIP();

    // Fallback to default after 1 second if detection fails
    setTimeout(() => {
        const urlDisplay = document.getElementById('connectionUrl');
        if (urlDisplay.textContent === 'Generating QR code...') {
            updateQRCode();
        }
    }, 1000);
});
