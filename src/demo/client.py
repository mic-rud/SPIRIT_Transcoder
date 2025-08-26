import numpy as np
import time
import asyncio
import json
import os
import yaml
import websockets
import multiprocessing as mp
from typing import Optional, Dict, Any

from player import Player
from decoder import DecoderPool



class DemoClient:
    def __init__(
        self,
        ws_url: str,
        coding_config: Dict[str, Any],
    ):
        self.ws_url = ws_url
        self.coding_config = coding_config 
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

        # Decoder
        self.decoder_pool = DecoderPool(num_workers=2)
        self.decoder_pool.start()

        # Player
        self.player_process = mp.Process(
            target=self._start_player,
            args=(self.decoder_pool.out_queue,), 
            daemon=True,
        )
        self.player_process.start()


    def _start_player(self, buffer):
        player = Player(buffer, ws_port=8765, target_fps=30)
        player.start()

    async def _connect(self, retries=10):
        """
        Routine for connecting to the websocket. 
        """
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
        """
        Send a json through the websocket
        """
        assert self._ws is not None
        await self._ws.send(json.dumps(payload))

    async def adjust_config(self, config: Dict[str, Any]):
        """
        Adjust server processing parameters at any time.
        """
        await self._send_json({
            "type": "AdjustConfig",
            "coding_config": config,
            "sequence": "longdress",
        })

    def _handle_decoded_frames(self, decoded):
        for frame in decoded:
            self.buffer.add_frame(frame)

    async def _recv_data(self):
        """
        Receive raw data
        """
        count = 0
        while True:
            print("[client] Waiting for a new message", flush=True)
            msg = await self._ws.recv()
            print("[Client] Receive timestamp {}".format(time.time()))

            if not isinstance(msg, bytes):
                print(f"[Client] got JSON: {msg}", flush=True)
                continue
            
            count += 1

            self.decoder_pool.submit(msg)

            # TODO Dummy config adjustment
            coding_config = self.coding_config.copy()
            coding_config["geoQP"] = 16
            coding_config["attQP"] = 22
            await self.adjust_config(coding_config)


    async def run(self):
        """Entry point: connect, send initial config, receive frames."""
        # Setup
        await self._connect()
        await self.adjust_config(self.coding_config)

        # Run the loop
        await self._recv_data()


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