#!/bin/bash
set -euo pipefail

# ARVOS Web Viewer - Quick Start Script

echo "🚀 Starting ARVOS Web Viewer..."
echo ""

# Detect ports (defaults: HTTP 8000, WebSocket 8765)
PORT="${1:-8000}"
WS_PORT="${2:-8765}"

# Get local IP
if command -v ifconfig &> /dev/null; then
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
elif command -v ip &> /dev/null; then
    LOCAL_IP=$(ip addr | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -n1)
else
    LOCAL_IP="localhost"
fi

echo "📡 Network Configuration:"
echo "   Local IP: $LOCAL_IP"
echo "   HTTP Port: $PORT"
echo "   WebSocket Port: $WS_PORT"
echo ""
echo "📱 iPhone Setup:"
echo "   1. Open ARVOS app"
echo "   2. Go to Stream tab"
echo "   3. Tap 'Connect to Server'"
echo "   4. Scan QR code from browser"
echo ""
echo "🌐 Opening browser at: http://$LOCAL_IP:$PORT"
echo ""
echo "⚠️  IMPORTANT: Use the IP address in your browser, not localhost!"
echo "   This allows automatic QR code generation."
echo ""

# Try to open browser automatically with IP address
if command -v open &> /dev/null; then
    # macOS
    sleep 2 && open "http://$LOCAL_IP:$PORT" &
elif command -v xdg-open &> /dev/null; then
    # Linux
    sleep 2 && xdg-open "http://$LOCAL_IP:$PORT" &
elif command -v start &> /dev/null; then
    # Windows
    sleep 2 && start "http://$LOCAL_IP:$PORT" &
fi

# Start ARVOS WebSocket server in background
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_SERVER_SCRIPT="$SCRIPT_DIR/ws-server.py"

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3."
    exit 1
fi

if [ ! -f "$WS_SERVER_SCRIPT" ]; then
    echo "❌ Error: WebSocket helper script not found at $WS_SERVER_SCRIPT"
    exit 1
fi

echo "🔌 Launching ARVOS WebSocket server..."
python3 "$WS_SERVER_SCRIPT" --port "$WS_PORT" &
WS_PID=$!

cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    if ps -p $WS_PID > /dev/null 2>&1; then
        kill $WS_PID 2>/dev/null || true
        wait $WS_PID 2>/dev/null || true
    fi
    echo "✅ Shutdown complete"
}

trap cleanup EXIT INT TERM

# Start HTTP server (try Python 3 first, then Python 2, then fail)
if command -v python3 &> /dev/null; then
    echo "✅ Starting Python 3 HTTP server..."
    python3 -m http.server "$PORT"
elif command -v python &> /dev/null; then
    echo "✅ Starting Python 2 HTTP server..."
    python -m SimpleHTTPServer "$PORT"
else
    echo "❌ Error: Python not found"
    echo ""
    echo "Please install Python 3:"
    echo "   macOS: brew install python3"
    echo "   Ubuntu: sudo apt install python3"
    echo "   Windows: https://python.org/downloads"
    exit 1
fi
