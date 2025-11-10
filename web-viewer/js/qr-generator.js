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

async function detectLocalIP() {
    console.log('Starting IP detection...');

    // Method 1: Try to get IP from window.location.hostname
    const hostname = window.location.hostname;
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && hostname !== '') {
        // Check if it's an IP address
        const ipRegex = /^([0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (ipRegex.test(hostname)) {
            console.log('IP from hostname:', hostname);
            updateQRCode(hostname);
            return;
        }
    }

    // Method 2: WebRTC IP detection
    const RTCPeerConnection = window.RTCPeerConnection ||
                               window.webkitRTCPeerConnection ||
                               window.mozRTCPeerConnection;

    if (!RTCPeerConnection) {
        console.warn('WebRTC not supported, cannot detect IP');
        // Try to use hostname or ask user
        promptForIP();
        return;
    }

    try {
        const pc = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        });

        pc.createDataChannel('');

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        let ipFound = false;

        pc.onicecandidate = (ice) => {
            if (!ice || !ice.candidate || !ice.candidate.candidate) {
                if (!ipFound) {
                    setTimeout(() => {
                        if (!ipFound) {
                            console.warn('No IP detected via WebRTC');
                            pc.close();
                            promptForIP();
                        }
                    }, 3000);
                }
                return;
            }

            const candidate = ice.candidate.candidate;
            console.log('ICE candidate:', candidate);

            // Match IPv4 addresses, but exclude 127.0.0.1
            const ipRegex = /([0-9]{1,3}\.){3}[0-9]{1,3}/g;
            const matches = candidate.match(ipRegex);

            if (matches) {
                for (const ip of matches) {
                    // Skip localhost and invalid IPs
                    if (ip !== '127.0.0.1' && !ip.startsWith('0.') && ip !== '0.0.0.0') {
                        console.log('✅ Detected IP:', ip);
                        ipFound = true;
                        updateQRCode(ip);
                        pc.close();
                        return;
                    }
                }
            }
        };

    } catch (error) {
        console.error('WebRTC detection failed:', error);
        promptForIP();
    }
}

function promptForIP() {
    // Show input field for manual IP entry
    const urlDisplay = document.getElementById('connectionUrl');
    const port = document.getElementById('customPort').value || '8765';

    // Create a more helpful message
    urlDisplay.innerHTML = `
        <div style="color: #f59e0b; font-size: 12px; margin-bottom: 10px;">
            ⚠️ Cannot auto-detect IP. Please enter manually:
        </div>
        <input type="text" id="manualIP" placeholder="e.g., 192.168.1.100"
               style="background: #1a1a1a; border: 1px solid #3b82f6; color: white;
                      padding: 8px; border-radius: 4px; width: 100%; font-family: monospace;"
               value="" />
    `;

    const input = document.getElementById('manualIP');
    input.focus();

    input.addEventListener('input', (e) => {
        const ip = e.target.value.trim();
        if (ip && /^([0-9]{1,3}\.){3}[0-9]{1,3}$/.test(ip)) {
            updateQRCode(ip);
        }
    });

    input.addEventListener('blur', (e) => {
        const ip = e.target.value.trim();
        if (ip && /^([0-9]{1,3}\.){3}[0-9]{1,3}$/.test(ip)) {
            updateQRCode(ip);
        } else if (!ip) {
            updateQRCode(null); // Use placeholder
        }
    });
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, starting IP detection...');

    // Try to detect IP
    detectLocalIP();

    // Fallback after 5 seconds if no IP detected
    setTimeout(() => {
        const urlDisplay = document.getElementById('connectionUrl');
        if (urlDisplay.textContent === 'Generating QR code...') {
            console.log('IP detection timeout, prompting for manual entry');
            promptForIP();
        }
    }, 5000);
});
