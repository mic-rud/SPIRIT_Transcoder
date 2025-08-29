import time
import multiprocessing
import numpy as np
import tmc2rs
from threading import Thread

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
    t_decode = end_time - start_time
    return frames, t_decode


def _worker_loop(in_q, result_queue):
    while True:
        item = in_q.get()
        if item is None:
            break
        task_id, msg = item
        try:
            frames, t_decode = decode_fn(msg)
            result_queue.put((task_id, t_decode, frames))
        except Exception as e:
            print(f"[Decoder Worker] Error: {e}", flush=True)


class DecoderPool:
    def __init__(self, num_workers, metrics):
        self.in_queue = multiprocessing.Queue(32)
        self.result_queue = multiprocessing.Queue(32)
        self.out_queue = multiprocessing.Queue(300)

        self.num_workers = num_workers
        self.procs = []
        self.next_task_id = 0
        self.expected_task_id = 0

        self.buffer = {}
        self.sorter_thread = None
        self.running = False

        self.metrics = metrics

    def start(self):
        self.running = True
        for _ in range(self.num_workers):
            p = multiprocessing.Process(
                target=_worker_loop,
                args=(self.in_queue, self.result_queue),
                daemon=True,
            )
            p.start()
            self.procs.append(p)

        self.sorter_thread = Thread(target=self._sorter_loop, daemon=True)
        self.sorter_thread.start()

    def submit(self, msg):
        self.in_queue.put((self.next_task_id, msg))
        self.next_task_id += 1

    async def stop(self):
        for _ in self.procs:
            self.in_queue.put(None)
        for p in self.procs:
            p.join()
        if self.sorter_thread:
            self.sorter_thread.join()


    def _sorter_loop(self):
        """
        Pulls completed jobs from result_queue, buffers them,
        and releases frames to out_queue in task order.
        """
        while self.running:
            task_id, t_decode, frames = self.result_queue.get()
            self.buffer[task_id] = frames
            self.metrics.set_t_decode(task_id, t_decode)

            # Emit all ready tasks in order
            while self.expected_task_id in self.buffer:
                frames = self.buffer.pop(self.expected_task_id)
                for frame in frames:
                    self.out_queue.put((self.expected_task_id, frame))
                self.expected_task_id += 1
            time.sleep(0.1)