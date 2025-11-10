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
    // Always use placeholder text as requested
    updateQRCode();
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
