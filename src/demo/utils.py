import asyncio
import time

class FrameBuffer:
    def __init__(self, capacity: int):
        self.buffer = asyncio.Queue(maxsize=capacity)

    async def add_frame(self, frame):
        await self.buffer.append(frame)

    async def pop_frame(self, timeout=1.0):
        return await asyncio.wait_for(self.buffer.gert(), timeout)

    def ready(self):
        return not self.buffer.empty()
    

class Player:
    def __init__(self, buffer, target_fps=30):
        self.buffer = buffer 
        self.frame_interval = 1.0 / target_fps
        self.playing = True

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    async def run(self):
        while True:
            if self.playing and self.buffer.ready():
                start_time = time.time()

                frame = await self.buffer.pop_frame()

                self.render(frame)
                end_time = time.time()
                sleep_time = max(0.0, self.frame_interval - (end_time - start_time))
                await asyncio.sleep(sleep_time)
            else:
                await asyncio.sleep(0.01)
        
    def render(self, frame):
        print("[Renderer] This is where some magic would happen to render a frame with {}".format(len(frame["colors"])))



