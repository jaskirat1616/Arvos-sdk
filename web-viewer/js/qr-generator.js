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
    const ip = getLocalIP();

    // ARVOS connection format: arvos://HOST:PORT
    const url = `arvos://${ip}:${port}`;
    return url;
}

function updateQRCode() {
    const canvas = document.getElementById('qrcode');
    const urlDisplay = document.getElementById('connectionUrl');
    const connectionURL = generateConnectionURL();

    // Clear previous QR code
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Generate new QR code
    QRCode.toCanvas(canvas, connectionURL, {
        width: 256,
        margin: 2,
        color: {
            dark: '#000000',
            light: '#FFFFFF'
        }
    }, function (error) {
        if (error) {
            console.error(error);
            urlDisplay.textContent = 'Error generating QR code';
            urlDisplay.style.color = '#ff4444';
        } else {
            urlDisplay.textContent = connectionURL;
            urlDisplay.style.color = '#666';
        }
    });
}

function goToViewer() {
    const port = document.getElementById('customPort').value || '8765';
    window.location.href = `viewer.html?port=${port}`;
}

function detectLocalIP() {
    // Try to detect local IP address for better UX
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
            // Update the QR code with detected IP
            const urlDisplay = document.getElementById('connectionUrl');
            const port = document.getElementById('customPort').value || '8765';
            const url = `arvos://${detectedIP}:${port}`;

            QRCode.toCanvas(document.getElementById('qrcode'), url, {
                width: 256,
                margin: 2,
                color: {
                    dark: '#000000',
                    light: '#FFFFFF'
                }
            });

            urlDisplay.textContent = url;
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
