#!/bin/bash
# Network diagnostics for ARVOS streaming

echo "🔍 ARVOS Network Diagnostics"
echo "============================="
echo ""

echo "📡 Mac Network Interfaces:"
echo "-------------------------"
ifconfig | grep "inet " | grep -v 127.0.0.1

echo ""
echo "📶 WiFi Network:"
echo "----------------"
/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport -I | grep " SSID" || echo "Not connected to WiFi"

echo ""
echo "🌐 WiFi IP Address:"
echo "-------------------"
WIFI_IP=$(ifconfig en0 | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}')
if [ -z "$WIFI_IP" ]; then
    echo "❌ No WiFi IP found!"
    echo "   Try: ifconfig en1 (if en0 doesn't work)"
else
    echo "✅ $WIFI_IP"
fi

echo ""
echo "🔌 Port 17500 Status:"
echo "---------------------"
if lsof -i :17500 > /dev/null 2>&1; then
    echo "✅ Port 17500 is in use (server running)"
    lsof -i :17500
else
    echo "❌ Port 17500 is free (server not running)"
    echo "   Start with: python3 examples/mcap_http_server.py"
fi

echo ""
echo "🧪 Testing Local Connection:"
echo "----------------------------"
if curl -s http://localhost:17500/api/mcap/health > /dev/null 2>&1; then
    echo "✅ Server responds locally"
    curl -s http://localhost:17500/api/mcap/health
else
    echo "❌ Server not responding locally"
    echo "   Make sure server is running!"
fi

echo ""
echo "🧪 Testing WiFi Connection:"
echo "---------------------------"
if [ ! -z "$WIFI_IP" ]; then
    if curl -s http://$WIFI_IP:17500/api/mcap/health > /dev/null 2>&1; then
        echo "✅ Server responds via WiFi IP"
        curl -s http://$WIFI_IP:17500/api/mcap/health
    else
        echo "❌ Server not responding via WiFi IP"
        echo "   Check firewall settings!"
    fi
else
    echo "⚠️  No WiFi IP to test"
fi

echo ""
echo "📱 iOS App Connection Settings:"
echo "-------------------------------"
if [ ! -z "$WIFI_IP" ]; then
    echo "Protocol: MCAP Stream"
    echo "Host/IP:  $WIFI_IP"
    echo "Port:     17500"
    echo ""
    echo "Health Check URL (test in iOS Safari):"
    echo "http://$WIFI_IP:17500/api/mcap/health"
else
    echo "❌ Cannot determine connection settings (no WiFi IP)"
fi

echo ""
echo "🔥 Firewall Status:"
echo "-------------------"
if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
    echo "⚠️  Firewall is ENABLED"
    echo "   You may need to allow Python incoming connections"
    echo "   System Preferences → Security & Privacy → Firewall"
else
    echo "✅ Firewall is disabled (good for testing)"
fi

echo ""
echo "✅ Diagnostics Complete!"
echo ""
echo "Next steps:"
echo "1. Make sure server is running: python3 examples/mcap_http_server.py"
echo "2. Make sure iOS device is on same WiFi network"
echo "3. Use IP address shown above in iOS app"
