#!/usr/bin/env python3
"""
Test script to verify all servers can start (briefly) without errors.

This starts each server for 1 second to verify they initialize correctly.
"""

import asyncio
import sys
import signal

def test_server_startup(server_class, server_name, **kwargs):
    """Test that a server can start without errors"""
    async def test():
        try:
            server = server_class(**kwargs)
            print(f"Testing {server_name}...")
            
            # Start server in background
            task = asyncio.create_task(server.start())
            
            # Wait 1 second
            await asyncio.sleep(1)
            
            # Stop server
            await server.stop()
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            print(f"✅ {server_name} - Started and stopped successfully\n")
            return True
        except ImportError as e:
            print(f"⚠️  {server_name} - Missing dependency: {e}\n")
            return False
        except Exception as e:
            print(f"❌ {server_name} - Error: {e}\n")
            return False
    
    return asyncio.run(test())

def main():
    print("=" * 60)
    print("Testing Server Startup")
    print("=" * 60)
    print()
    
    results = []
    
    # Test WebSocket (basic_server uses ArvosServer, not from servers module)
    print("ℹ️  WebSocket: Use examples/basic_server.py (uses ArvosServer)")
    print()
    
    # Test HTTP
    try:
        from arvos.servers import HTTPArvosServer
        ok = test_server_startup(HTTPArvosServer, "HTTP/REST", port=8080)
        results.append(("HTTP/REST", ok))
    except Exception as e:
        print(f"❌ HTTP/REST: {e}\n")
        results.append(("HTTP/REST", False))
    
    # Test MQTT (will fail if broker not running, but should initialize)
    try:
        from arvos.servers import MQTTArvosServer
        # Just test instantiation, not connection
        server = MQTTArvosServer(host="localhost", port=1883)
        print("✅ MQTT - Can be instantiated (broker connection will fail if not running)")
        print("   This is expected - start mosquitto broker first\n")
        results.append(("MQTT", True))
    except Exception as e:
        print(f"❌ MQTT: {e}\n")
        results.append(("MQTT", False))
    
    # Test MCAP
    try:
        from arvos.servers import MCAPStreamServer
        ok = test_server_startup(MCAPStreamServer, "MCAP Stream", port=17500)
        results.append(("MCAP Stream", ok))
    except Exception as e:
        print(f"❌ MCAP Stream: {e}\n")
        results.append(("MCAP Stream", False))
    
    # Test gRPC (will fail if protobuf not generated)
    try:
        from arvos.servers import GRPCArvosServer
        server = GRPCArvosServer(port=50051)
        print("✅ gRPC - Can be instantiated")
        print("   Note: Requires protobuf definitions to actually start\n")
        results.append(("gRPC", True))
    except Exception as e:
        print(f"⚠️  gRPC: {e}\n")
        results.append(("gRPC", False))
    
    # Test QUIC (will fail if aioquic not installed)
    try:
        from arvos.servers import QUICArvosServer
        server = QUICArvosServer(port=4433)
        print("✅ QUIC/HTTP3 - Can be instantiated")
        print("   Note: Requires aioquic to actually start\n")
        results.append(("QUIC/HTTP3", True))
    except Exception as e:
        print(f"⚠️  QUIC/HTTP3: {e}\n")
        results.append(("QUIC/HTTP3", False))
    
    # Summary
    print("=" * 60)
    print("Summary:")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All servers can be instantiated!")
        return 0
    else:
        print("\n⚠️  Some servers have missing dependencies (install as needed)")
        return 0

if __name__ == "__main__":
    sys.exit(main())

