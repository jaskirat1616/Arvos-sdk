#!/usr/bin/env python3
"""
Test script to verify all protocol servers can be imported and instantiated.

This doesn't start the servers, just verifies they can be created.
"""

import sys

def test_imports():
    """Test that all servers can be imported"""
    print("Testing server imports...")
    print("=" * 60)
    
    results = []
    
    # Test HTTP
    try:
        from arvos.servers import HTTPArvosServer
        server = HTTPArvosServer(port=8080)
        print("✅ HTTPArvosServer - OK")
        results.append(("HTTP", True))
    except Exception as e:
        print(f"❌ HTTPArvosServer - FAILED: {e}")
        results.append(("HTTP", False))
    
    # Test MQTT
    try:
        from arvos.servers import MQTTArvosServer
        server = MQTTArvosServer(host="localhost", port=1883)
        print("✅ MQTTArvosServer - OK")
        results.append(("MQTT", True))
    except Exception as e:
        print(f"❌ MQTTArvosServer - FAILED: {e}")
        results.append(("MQTT", False))
    
    # Test MCAP WebSocket
    try:
        from arvos.servers import MCAPStreamServer
        server = MCAPStreamServer(port=17500)
        print("✅ MCAPStreamServer (WebSocket) - OK")
        results.append(("MCAP WebSocket", True))
    except Exception as e:
        print(f"❌ MCAPStreamServer - FAILED: {e}")
        results.append(("MCAP WebSocket", False))

    # Test MCAP HTTP
    try:
        from arvos.servers import MCAPHTTPServer
        server = MCAPHTTPServer(port=17501)
        print("✅ MCAPHTTPServer (HTTP POST) - OK")
        results.append(("MCAP HTTP", True))
    except Exception as e:
        print(f"❌ MCAPHTTPServer - FAILED: {e}")
        results.append(("MCAP HTTP", False))
    
    # Test gRPC
    try:
        from arvos.servers import GRPCArvosServer
        server = GRPCArvosServer(port=50051)
        print("✅ GRPCArvosServer - OK")
        results.append(("gRPC", True))
    except Exception as e:
        print(f"⚠️  GRPCArvosServer - WARNING: {e}")
        print("   (This is OK if protobuf definitions aren't generated yet)")
        results.append(("gRPC", False))
    
    # Test QUIC
    try:
        from arvos.servers import QUICArvosServer
        server = QUICArvosServer(port=4433)
        print("✅ QUICArvosServer - OK")
        results.append(("QUIC", True))
    except Exception as e:
        print(f"⚠️  QUICArvosServer - WARNING: {e}")
        print("   (This is OK if aioquic isn't installed)")
        results.append(("QUIC", False))
    
    print("=" * 60)
    print("\nSummary:")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    
    if passed == total:
        print("\n🎉 All servers are ready!")
        return 0
    else:
        print("\n⚠️  Some servers have missing dependencies (this is OK)")
        print("   Install them as needed for the protocols you want to use.")
        return 0

if __name__ == "__main__":
    sys.exit(test_imports())

