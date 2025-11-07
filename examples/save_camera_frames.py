#!/usr/bin/env python3
"""
Save camera frames to disk

This example saves camera frames as JPEG images and creates a video.

Requirements:
    pip install Pillow opencv-python

Usage:
    python save_camera_frames.py
"""

import asyncio
from pathlib import Path
from datetime import datetime
from arvos import ArvosServer, CameraFrame

try:
    from PIL import Image
    import io
    import cv2
    import numpy as np
except ImportError:
    print("Error: This example requires Pillow and opencv-python")
    print("Install with: pip install Pillow opencv-python")
    exit(1)


async def main():
    # Create output directory
    output_dir = Path(f"arvos_camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)

    print(f"📁 Saving camera frames to: {output_dir}")

    # Video writer
    video_writer = None
    frame_count = 0

    server = ArvosServer(port=9090)

    # Handle camera frames
    async def on_camera(frame: CameraFrame):
        nonlocal video_writer, frame_count

        frame_count += 1

        # Decode JPEG
        image = Image.open(io.BytesIO(frame.data))
        img_array = np.array(image)

        # Save every 10th frame as JPEG
        if frame_count % 10 == 0:
            image_path = output_dir / f"frame_{frame_count:06d}.jpg"
            image.save(image_path)
            print(f"📷 Saved frame {frame_count}: {image_path.name}")

        # Initialize video writer on first frame
        if video_writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_path = str(output_dir / "camera_video.mp4")
            fps = 10  # Approximate FPS
            video_writer = cv2.VideoWriter(
                video_path,
                fourcc,
                fps,
                (frame.width, frame.height)
            )
            print(f"🎥 Starting video recording: {video_path}")

        # Write frame to video (convert RGB to BGR for OpenCV)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        video_writer.write(img_bgr)

        if frame_count % 30 == 0:
            print(f"🎬 Video frames written: {frame_count}")

    # Handle disconnection
    async def on_disconnect(client_id: str):
        print(f"\n💾 Finalizing video...")
        if video_writer:
            video_writer.release()
        print(f"✅ Saved {frame_count} frames to {output_dir}")

    server.on_camera = on_camera
    server.on_disconnect = on_disconnect

    print("🚀 Starting server...")
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
        if video_writer:
            video_writer.release()


if __name__ == "__main__":
    asyncio.run(main())
