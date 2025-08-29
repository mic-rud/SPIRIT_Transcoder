import numpy as np
import time
import asyncio
import json
import os
import yaml
import websockets
import msgpack
import threading
import multiprocessing as mp
from typing import Optional, Dict, Any

from player import Player
from decoder import DecoderPool
from gui.backend import create_flask_app


class Metrics:
    def __init__(self):
        self.t_transcode = {}
        self.t_decode = {}
        self.bandwidth = {}

    def get_metrics(self, idx):
        if any(idx not in x.keys() for x in (self.t_decode, self.t_transcode, self.bandwidth)):
            return None

        t_transcode = self.t_transcode.pop(idx) if idx in self.t_transcode.keys() else None
        t_decode = self.t_decode.pop(idx) if idx in self.t_decode.keys() else None
        bandwidth = self.bandwidth.pop(idx) if idx in self.bandwidth.keys() else None

        metrics = {
            "t_transcode": t_transcode,
            "t_decode": t_decode,
            "bandwidth": bandwidth,
        }

        return metrics

    def set_t_transcode(self, idx, t_transcode):
        self.t_transcode[idx] = t_transcode

    def set_t_decode(self, idx, t_decode):
        self.t_decode[idx] = t_decode

    def set_bandwidth(self, idx, bandwidth):
        self.bandwidth[idx] = bandwidth
        

class DemoClient:
    def __init__(
        self,
        ws_url: str,
        coding_config: Dict[str, Any],
    ):
        self.ws_url = ws_url
        self.coding_config = coding_config 
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

        self.metrics = Metrics()

        # Decoder
        self.decoder_pool = DecoderPool(num_workers=4, metrics=self.metrics)
        self.decoder_pool.start()

        # Player
        self.player_process = mp.Process(
            target=self._start_player,
            args=(self.decoder_pool.out_queue,), 
            daemon=True,
        )
        self.player_process.start()


    def _start_player(self, buffer):
        player = Player(buffer, ws_port=8765, target_fps=15)
        player.start()

    async def _connect(self, retries=10):
        """
        Routine for connecting to the websocket. 
        """
        await asyncio.sleep(2.0)
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
        seq = config.pop("sequence")
        self.coding_config["geoQP"] = config["geoQP"]
        self.coding_config["attQP"] = config["attQP"]

        await self._send_json({
            "type": "AdjustConfig",
            "coding_config": self.coding_config,
            "sequence": seq,
        })


    async def _recv_data(self):
        """
        Receive raw data
        """
        count = 0
        while True:
            payload = await self._ws.recv()

            if not isinstance(payload, bytes):
                continue
            
            msg = msgpack.unpackb(payload, raw=False)
            data = msg["data"]
            t_transcode = msg["t_transcode"]

            self.metrics.set_t_transcode(count, t_transcode)
            self.metrics.set_bandwidth(count, len(data))

            count += 1

            self.decoder_pool.submit(data)


    async def run(self):
        """Entry point: connect, send initial config, receive frames."""
        # Setup
        await self._connect()

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
    base_config["sequence"] = "loot"
    client = DemoClient( url, base_config)

    app, socketio = create_flask_app(client)
    threading.Thread(
        target=lambda: socketio.run(
            app, 
            host="0.0.0.0", 
            port=5000,
            allow_unsafe_werkzeug=True,
            use_reloader=False,
        ),
        daemon=True
    ).start()

    # Run the client
    asyncio.run(client.run())
