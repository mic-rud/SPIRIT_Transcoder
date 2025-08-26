import asyncio
import websockets
import numpy as np
import struct
import time
import multiprocessing as mp


class Player:
    def __init__(self, buffer, ws_port=8765, target_fps=30):
        self.buffer = buffer
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.ws_port = ws_port

        # FPS tracking
        self.fps_ema_alpha = 0.1
        self.actual_fps = float(target_fps)

    def pack_frame(self, frame):
        """
        Pack a single frame into a binary blob for WebSocket streaming.
        Format: [x,y,z float32]*N + [r,g,b uint8]*N
        """
        positions = frame["positions"].astype(np.float32)
        colors = (frame["colors"] * 255).astype(np.uint8)
        return positions.tobytes() + colors.tobytes()

    async def websocket_handler(self, websocket):
        """
        Send frames to a connected WebSocket client.
        """
        print("[WebSocket] Client connected")
        prev_frame_time = time.time()

        try:
            while True:
                frame_package = self.buffer.get()
                if frame_package is None:
                    print("[Player] Shutting down WebSocket")
                    break

                frame_id, frame = frame_package
                packed = self.pack_frame(frame)

                # Send frame to browser
                await websocket.send(packed)
                print(f"[Player] Sent frame {frame_id} with {len(frame['positions'])} points", flush=True)

                # FPS control
                prev_frame_time = self.fps_monitor(prev_frame_time)
        except websockets.exceptions.ConnectionClosed:
            print("[WebSocket] Client disconnected")

    def fps_monitor(self, prev_frame_time):
        """
        Monitor FPS and apply frame rate control.
        """
        now = time.time()
        sleep_time = max(0.0, self.frame_interval - (now - prev_frame_time))

        frame_time = max(sleep_time, time.time() - prev_frame_time)
        self.actual_fps = (
            self.fps_ema_alpha * (1.0 / frame_time)
            + (1 - self.fps_ema_alpha) * self.actual_fps
        )
        print(f"[Player] FPS: {self.actual_fps:.2f} | Frame Time: {frame_time:.2f}s")

        time.sleep(sleep_time)
        return now

    async def run_ws_server(self):
        """
        Start the WebSocket server and wait for client connections.
        """
        print(f"[WebSocket] Starting server on ws://0.0.0.0:{self.ws_port}")
        async with websockets.serve(self.websocket_handler, "0.0.0.0", self.ws_port, max_size=None):
            await asyncio.Future()  # Keep server alive

    def start(self):
        """
        Entry point for running the player in async mode.
        """
        asyncio.run(self.run_ws_server())