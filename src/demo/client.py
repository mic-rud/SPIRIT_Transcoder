import time
import asyncio
import json
import os
import yaml
import websockets
from threading import Thread
import multiprocessing
from typing import Optional, Dict, Any
from utils import FrameBuffer, Player

import tmc2rs
import tempfile
import os

import concurrent.futures


def decode_frames(msg: bytes, max_frames: int = 15):
    t0 = time.time()
    decoder = tmc2rs.PyTMC2Decoder(msg)
    frames = []

    for _ in range(max_frames):
        frame = decoder.next_frame()
        if frame is None:
            break
        frames.append(frame)

    decoder.close()
    print("Time decoder {}".format(time.time() - t0), flush=True)
    return frames

class DemoClient:
    def __init__(
        self,
        ws_url: str,
        coding_config: Dict[str, Any],
    ):
        self.ws_url = ws_url
        self.coding_config = coding_config 
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

        self.buffer = FrameBuffer(capacity=100)
        self.player = Player(self.buffer, target_fps=30)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.pool = multiprocessing.Pool(processes=4)

    async def _connect(self):
        """
        
        """
        retries = 10
        for attempt in range(retries):
            try:
                self._ws = await websockets.connect(self.ws_url, max_size=None)
                print(f"[client] Connected to {self.ws_url}")
                return
            except (ConnectionRefusedError, OSError) as e:
                print(f"[client] Retry {attempt+1}/{retries}: {e}")
                await asyncio.sleep(1.0)
        raise RuntimeError(f"[client] Failed to connect after {retries} retries.")


    async def _send_json(self, payload: Dict[str, Any]):
        assert self._ws is not None, "WebSocket not connected"
        await self._ws.send(json.dumps(payload))

    async def adjust_config(self, config: Dict[str, Any]):
        """Adjust server processing parameters at any time."""
        await self._send_json({
            "type": "AdjustConfig",
            "coding_config": config,
            "sequence": "loot",
        })

    async def _send_initial_config(self):
        await self.adjust_config(self.coding_config)

    def decode_and_buffer(self, msg, num_frames=15):
        t0 = time.time()
        decoder = tmc2rs.PyTMC2Decoder(msg)

        try:
            count = 0
            while count < num_frames:
                frame = decoder.next_frame()
                print("[Decoder  frame {} received ]".format(count))
                if frame is None:
                    print("[Decoder end of stream a frame {}]".format(count), flush=True)
                    break
                count += 1
                self.buffer.add_frame(frame)

            elapsed = time.time() - t0
            print("[Decoder closed in {}s]".format(elapsed))
            decoder.close()

        except Exception as e:
            print(f"[Decoder] failed to decode frame - {e}")


    async def handle_decoded_frames(self, result):
        for frame in result:
            await self.buffer.add_frame(frame)


    async def _recv_data(self):
        """Receive raw data"""
        assert self._ws is not None
        count = 0
        try:
            while True:
                print("[client] Waiting for a new message", flush=True)
                msg = await self._ws.recv()
                print("[client] Message received", flush=True)
                if isinstance(msg, bytes):
                    print("[Client] Receive timestamp {}".format(time.time()))
                    import hashlib
                    print(f"[RX] {len(msg)} bytes sha256={hashlib.sha256(msg).hexdigest()} at {time.time()}")

                    count += 1

                    #Thread(target=self.decode_and_buffer, args=(msg,), daemon=True).start()
                    #self.executor.submit(self.decode_and_buffer, msg)
                    self.pool.apply_async(decode_frames, args=(msg,), callback=self.handle_decoded_frames)
                    
                    # TODO Dummy config adjustment
                    coding_config = self.coding_config
                    coding_config["geoQP"] = 40 % (count + 1) +10
                    coding_config["attQP"] = 40 % (count + 1) + 10
                    await self.adjust_config(coding_config)

                    print("[Client] Config adjusted")
                else:
                    print(f"[Client] got JSON: {msg}", flush=True)

                # Send config
        except websockets.ConnectionClosed:
            print("[Client] connection closed by server")

    async def run(self):
        """Entry point: connect, send initial config, receive frames."""
        await self._connect()

        asyncio.create_task(self.player.run())

        try:
            await self._send_initial_config()
            await self._recv_data()
        finally:
            if self._ws is not None:
                await self._ws.close()
                print("[Client] closed")

if __name__ == "__main__":
    url = os.getenv("WS_URL", "ws://server:8000/ws")

    config_path = "/app/configs/demo_config.yaml"
    with open(config_path, "r") as f:
        base_config = yaml.safe_load(f)

    # Load rate config
    rate_config_path = base_config.get("rate-config", "rate/R1.yaml")
    with open(rate_config_path, "r") as f:
        rate_config = yaml.safe_load(f)

    base_config.update(rate_config)
    asyncio.run(DemoClient(
        url,
        base_config
        ).run())