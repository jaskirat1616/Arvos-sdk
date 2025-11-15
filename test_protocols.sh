#!/bin/bash
# Interactive protocol testing script for ARVOS

echo "🧪 ARVOS Protocol Testing Suite"
echo "================================"
echo ""
echo "Select a protocol to test:"
echo ""
echo "  1) HTTP/REST (port 8080)"
echo "  2) MCAP HTTP Stream (port 17500) ⭐ RECOMMENDED for iOS"
echo "  3) MCAP WebSocket Stream (port 17500)"
echo "  4) MQTT (port 1883)"
echo "  5) QUIC/HTTP3 (port 4433)"
echo "  6) gRPC (port 50051)"
echo "  7) Test all protocols availability"
echo "  8) View testing guide"
echo "  q) Quit"
echo ""
read -p "Enter choice [1-8, q]: " choice

case $choice in
    1)
        echo "🚀 Starting HTTP/REST server..."
        python3 examples/http_stream_server.py
        ;;
    2)
        echo "🚀 Starting MCAP HTTP server..."
        echo "💡 Use this with iOS app's 'MCAP Stream' protocol"
        python3 examples/mcap_http_server.py
        ;;
    3)
        echo "🚀 Starting MCAP WebSocket server..."
        echo "⚠️  Note: iOS MCAP adapter uses HTTP, not WebSocket"
        echo "   For iOS, use option 2 instead"
        python3 examples/mcap_stream_server.py
        ;;
    4)
        echo "🚀 Starting MQTT server..."
        echo "⚠️  Make sure mosquitto broker is running:"
        echo "   brew install mosquitto"
        echo "   mosquitto -v"
        python3 examples/mqtt_stream_server.py
        ;;
    5)
        echo "🚀 Starting QUIC/HTTP3 server..."
        python3 examples/quic_stream_server.py
        ;;
    6)
        echo "🚀 Starting gRPC server..."
        python3 examples/grpc_stream_server.py
        ;;
    7)
        echo "🧪 Testing all protocol availability..."
        python3 examples/test_all_protocols.py
        ;;
    8)
        echo "📖 Opening testing guide..."
        if command -v bat &> /dev/null; then
            bat TEST_ALL_PROTOCOLS.md
        elif command -v less &> /dev/null; then
            less TEST_ALL_PROTOCOLS.md
        else
            cat TEST_ALL_PROTOCOLS.md
        fi
        ;;
    q|Q)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
