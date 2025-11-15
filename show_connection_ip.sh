#!/bin/bash
# Show the correct IP address for iOS connection

echo "🔍 Finding correct connection IP..."
echo ""

# Check for USB interface (usually starts with 169.254 or 172.20)
USB_IP=$(ifconfig | grep "inet " | grep -E "169\.254\.|172\.20\." | awk '{print $2}' | head -1)

if [ ! -z "$USB_IP" ]; then
    echo "✅ USB Connection Found!"
    echo "   Interface IP: $USB_IP"
    echo ""
    echo "📱 iOS App Settings:"
    echo "   Protocol: MCAP Stream"
    echo "   Host: $USB_IP"
    echo "   Port: 17500"
    echo ""

    # Test if server is running
    if curl -s http://$USB_IP:17500/api/mcap/health > /dev/null 2>&1; then
        echo "✅ Server is reachable at http://$USB_IP:17500"
        echo ""
        echo "🎉 Ready to connect!"
    else
        echo "⚠️  Server not responding"
        echo "   Make sure server is running:"
        echo "   python3 examples/mcap_http_server.py"
    fi
else
    echo "❌ No USB connection found"
    echo ""
    echo "   Available IPs:"
    ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print "   - " $2}'
    echo ""
    echo "   Try connecting iPhone via USB and enabling Personal Hotspot"
fi

echo ""
echo "💡 Alternative: Try using 'localhost' in iOS app"
