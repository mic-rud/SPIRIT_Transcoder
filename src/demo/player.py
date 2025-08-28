import os
import zmq
import zmq.asyncio
import asyncio
import numpy as np
import struct
import time
import multiprocessing as mp


class Player:
    def __init__(self, buffer, ws_port=8765, target_fps=30):
        self.buffer = buffer
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps

        # FPS tracking
        self.fps_ema_alpha = 0.1
        self.actual_fps = float(target_fps)

        zmq_push_addr = os.getenv("ZMQ_PUSH_SOCKET")
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.connect(zmq_push_addr)

    def pack_frame(self, frame):
        """
        Pack a single frame into a binary blob for 
        Format: [x,y,z float32]*N + [r,g,b uint8]*N
        """
        positions = frame["positions"].astype(np.float16)
        colors = 255 - (frame["colors"] * 255).astype(np.uint8)
        return positions.tobytes() + colors.tobytes()

    async def render_loop(self):
        """
        Send frames to a connected 
        """
        prev_frame_time = time.time()

        while True:
            frame_package = self.buffer.get()
            if frame_package is None:
                print("[Player] Shutting down Renderer")
                break

            frame_id, frame = frame_package
            packed = self.pack_frame(frame)

            # Send frame to browser
            await self.zmq_socket.send(packed)
            #print(f"[Player] Sent frame {frame_id} with {len(frame['positions'])} points", flush=True)

            # FPS control
            prev_frame_time = self.fps_monitor(prev_frame_time)

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
        #print(f"[Player] FPS: {self.actual_fps:.2f} | Frame Time: {frame_time:.2f}s")

        time.sleep(sleep_time)
        return now


    def start(self):
        """
        Entry point for running the player in async mode.
        """
        asyncio.run(self.render_loop())