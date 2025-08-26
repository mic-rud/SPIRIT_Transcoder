import time
import multiprocessing
import numpy as np
import tmc2rs

def decode_fn(msg: bytes, max_frames: int = 15):
    """Decode V3C bitstream into frames."""
    start_time = time.time()
    decoder = tmc2rs.PyTMC2Decoder(msg)
    frames = []
    for i in range(max_frames):
        frame = decoder.next_frame()
        if frame is None:
            break
        frames.append({
            "positions": np.array(frame["positions"]),
            "colors": np.array(frame["colors"]),
        })
    decoder.close()
    end_time = time.time()
    print("[Decoder] Decoded in {} s ".format(end_time - start_time), flush=True)
    return frames


def _worker_loop(in_q, out_q):
    while True:
        item = in_q.get()
        if item is None:
            break
        task_id, msg = item
        try:
            frames = decode_fn(msg)
            for frame in frames:
                out_q.put((task_id, frame))
        except Exception as e:
            print(f"[Decoder Worker] Error: {e}", flush=True)


class DecoderPool:
    def __init__(self, num_workers):
        self.in_queue = multiprocessing.Queue(32)
        self.out_queue = multiprocessing.Queue(300)
        self.procs = []
        self.next_task_id = 0
        self.num_workers = num_workers

    def start(self):
        for _ in range(self.num_workers):
            p = multiprocessing.Process(
                target=_worker_loop,
                args=(self.in_queue, self.out_queue),
                daemon=True,
            )
            p.start()
            self.procs.append(p)

    def submit(self, msg):
        self.in_queue.put((self.next_task_id, msg))
        self.next_task_id += 1

    async def stop(self):
        for _ in self.procs:
            self.in_queue.put(None)
        for p in self.procs:
            p.join()
