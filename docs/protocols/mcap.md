# MCAP Stream Protocol

Robotics standard format - perfect for Foxglove Studio and robotics research.

## Overview

MCAP (Modular Container for Arbitrary Protocols) provides:
- ✅ Robotics standard format
- ✅ Foxglove Studio compatible
- ✅ Streaming MCAP files
- ✅ Standardized metadata

## Default Port

**17500**

## Requirements

### Python
```bash
pip install mcap
```

## Quick Start

### Python Server

```python
import asyncio
from arvos.servers import MCAPStreamServer

async def main():
    server = MCAPStreamServer(
        host="0.0.0.0",
        port=17500,
        output_file="output.mcap"
    )
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **MCAP Stream** protocol
3. Enter server IP and port 17500
4. Connect!

## Features

### Standard Format
- Robotics industry standard
- Compatible with many tools
- Well-documented format

### Foxglove Studio
- Direct playback in Foxglove
- Rich visualization
- Timeline navigation

### Streaming
- Real-time MCAP generation
- No post-processing needed
- Immediate playback

## Use Cases

- Robotics research
- Foxglove Studio visualization
- Standardized data collection
- Tool compatibility

## Advantages

- ✅ Industry standard
- ✅ Foxglove compatible
- ✅ Rich metadata
- ✅ Tool ecosystem

## Limitations

- ⚠️ Larger file sizes
- ⚠️ More complex format
- ⚠️ Requires MCAP tools

## Example

See [MCAP Example](../examples/protocols.md#mcap)

## Next Steps

- [Protocol Comparison](comparison.md)
- [Foxglove Studio](https://foxglove.dev) - Visualization tool

