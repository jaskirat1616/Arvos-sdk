#!/usr/bin/env python3
"""
Camera Viewer - Beautiful Glassy UI

Modern, minimal design with glass morphism.
Clean overlay with only essential information.

Usage:
    python camera_viewer_ui.py [--port 9090]
"""

import asyncio
import cv2
import numpy as np
from arvos import ArvosServer, CameraFrame
import time
import argparse


class GlassyCameraViewer:
    def __init__(self):
        self.latest_frame = None
        self.frame_count = 0
        self.fps = 0.0
        self.last_fps_time = time.time()

    def update_camera(self, frame: CameraFrame):
        """Fast camera decode"""
        try:
            img = cv2.imdecode(np.frombuffer(frame.data, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.latest_frame = img

            self.frame_count += 1
            now = time.time()
            if now - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (now - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = now

        except Exception as e:
            print(f"❌ Error: {e}")

    def draw_glassy_overlay(self, frame):
        """Draw beautiful minimal overlay with glass morphism"""
        h, w = frame.shape[:2]

        # Create overlay layer
        overlay = frame.copy()

        # Top bar - glassy background
        bar_height = 80
        bar_alpha = 0.15  # Very transparent for glass effect

        # Draw blur effect (fake glass)
        roi = frame[0:bar_height, 0:w]
        blurred = cv2.GaussianBlur(roi, (21, 21), 0)

        # Darken for contrast
        blurred = cv2.addWeighted(blurred, 0.6, np.zeros_like(blurred), 0.4, 0)

        # Place blurred region back
        frame[0:bar_height, 0:w] = blurred

        # Subtle top border (white, very thin)
        cv2.line(frame, (0, bar_height-1), (w, bar_height-1), (255, 255, 255), 1)

        # FPS indicator - minimal, white
        fps_text = f"{self.fps:.0f} FPS"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 2

        # Get text size for centering
        (text_w, text_h), _ = cv2.getTextSize(fps_text, font, font_scale, thickness)

        # Position: top-left with padding
        x = 30
        y = 50

        # Draw text with subtle shadow for depth
        # Shadow
        cv2.putText(frame, fps_text, (x+2, y+2), font, font_scale, (0, 0, 0), thickness+1, cv2.LINE_AA)
        # Main text (white)
        cv2.putText(frame, fps_text, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        # Bottom right corner - subtle status indicator
        status_text = "LIVE"
        status_font_scale = 0.5
        (status_w, status_h), _ = cv2.getTextSize(status_text, font, status_font_scale, 1)

        status_x = w - status_w - 30
        status_y = h - 25

        # Glassy pill background for status
        pill_padding = 12
        pill_x1 = status_x - pill_padding
        pill_y1 = status_y - status_h - pill_padding + 5
        pill_x2 = status_x + status_w + pill_padding
        pill_y2 = status_y + pill_padding

        # Draw pill (rounded rectangle)
        pill_overlay = frame.copy()
        cv2.rectangle(pill_overlay, (pill_x1, pill_y1), (pill_x2, pill_y2), (255, 255, 255), -1)
        frame = cv2.addWeighted(pill_overlay, 0.1, frame, 0.9, 0)

        # Pill border
        cv2.rectangle(frame, (pill_x1, pill_y1), (pill_x2, pill_y2), (255, 255, 255), 1)

        # Status text
        cv2.putText(frame, status_text, (status_x, status_y), font, status_font_scale, (255, 255, 255), 1, cv2.LINE_AA)

        return frame


async def main():
    parser = argparse.ArgumentParser(description='Arvos Camera Viewer - Glassy UI')
    parser.add_argument('--port', type=int, default=9090, help='Server port')
    args = parser.parse_args()

    print(f"📷 Camera Viewer - Glassy UI")

    viewer = GlassyCameraViewer()
    server = ArvosServer(port=args.port)

    server.on_camera = viewer.update_camera

    async def on_connect(client_id: str):
        print(f"✅ Connected")

    server.on_connect = on_connect
    server_task = asyncio.create_task(server.start())

    # Create named window with no toolbar
    cv2.namedWindow('Arvos', cv2.WINDOW_NORMAL)

    running = True
    while running:
        if viewer.latest_frame is not None:
            # Draw glassy overlay
            display_frame = viewer.draw_glassy_overlay(viewer.latest_frame.copy())
            cv2.imshow('Arvos', display_frame)
        else:
            # Minimal placeholder
            placeholder = np.zeros((720, 1280, 3), dtype=np.uint8)
            placeholder[:] = (25, 25, 25)  # Dark gray

            text = "Waiting for stream..."
            font = cv2.FONT_HERSHEY_SIMPLEX
            (text_w, text_h), _ = cv2.getTextSize(text, font, 1.0, 2)

            x = (1280 - text_w) // 2
            y = (720 + text_h) // 2

            cv2.putText(placeholder, text, (x, y), font, 1.0, (200, 200, 200), 2, cv2.LINE_AA)
            cv2.imshow('Arvos', placeholder)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # q or ESC
            running = False
            break

        await asyncio.sleep(0)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(main())
