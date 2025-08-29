import time
import asyncio
import os

from pydantic import BaseModel
from typing import Optional, List, Tuple, Dict
import msgpack

class WSCommand(BaseModel):
    type: str
    sequence: str
    coding_config: dict

class TranscodingService:
    def __init__(self, 
                 worker,
                 media_dir: str,
                 processed_dir: str,
                 segment_duration: float,
                 num_segments: int
                 ):
        # Data setup
        self.media_dir = media_dir
        self.processed_dir = processed_dir
        self.segment_duration = segment_duration
        self.num_segments = num_segments

        # Websocket client and loop state
        self.client = None
        self.running = False
        
        # Transcoder
        self.coding_config = {}
        self.worker = worker
        
        # Utilities
        self._cfg_lock = asyncio.Lock()
        self.start_time = time.monotonic()
        self.verbose = True

    def log(self, *args):
        if self.verbose:
            print("[Server][Transcoder]", *args, flush=True)

    def update_config(self, coding_config):
        """
        Update the current coding configuration.
        """
        self.log("Updated config")
        self.coding_config = coding_config


    def _process(self, in_path: str, out_path: str, config: Dict):
        """Run the transcoding process."""
        try:
            self.worker.transcode(in_path, out_path, config)
        except Exception as e:
            self.log(f"Transcoder FAILED: {e}")



    def _get_segment_paths(self, sequence: str, index: int) -> tuple[str, str]:
        """
        Get the segment paths of the current segment and the temporary output path
        """
        name = f"{sequence}_r5_segment{index}.bin"
        in_path = os.path.join(self.media_dir, name)
        out_path = os.path.join(self.processed_dir, name)
        return in_path, out_path

    async def _process_segment(self, segment_index):
        """
        Transcodes and sends a segment.
        """
        async with self._cfg_lock:
            config = dict(self.coding_config) 

        in_path, out_path = self._get_segment_paths(config["sequence"], segment_index)

        # Processing
        loop = asyncio.get_running_loop()
        t_start = time.time()
        await loop.run_in_executor(None, self._process, in_path, out_path, config["coding_config"])
        t_transcode = time.time() - t_start

        try:
            if self.client and os.path.exists(out_path):
                with open(out_path, "rb") as f: 
                    data = f.read()
       
                payload = msgpack.packb({"t_transcode": t_transcode, "data": data}, use_bin_type=True)

                await self.client.send_bytes(payload)
            else:
                self.log(f"Failed sending segment {segment_index}")

        # Clean up temp file
        finally:
            if os.path.exists(out_path):
                os.remove(out_path)

    async def start_loop(self):
        """
        Processing loop at running at segment_duration intervals
        """
        self.running = True
        segment_index = 0
        segment_counter = 0
        base_time = time.monotonic()

        while self.running:
            start_time = time.monotonic()
            segment_start_time = base_time + segment_counter * self.segment_duration

            await self._process_segment(segment_index)

            # Bookkeeping
            segment_counter += 1
            segment_index = (segment_index + 1) % self.num_segments

            # Timekeeping
            end_time = time.monotonic()
            sleep_time = max(0, segment_start_time + self.segment_duration - end_time)
            await asyncio.sleep(sleep_time)

    def stop(self):
        self.log("Stopping transcoding loop")
        self.running = False
