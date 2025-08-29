import asyncio
import websockets
import zmq
import zmq.asyncio

# ZeroMQ PULL socket setup
context = zmq.asyncio.Context()
zmq_socket = context.socket(zmq.PULL)
zmq_socket.bind("tcp://*:5556")  # Producer must use PUSH+CONNECT

# Adjustable settings
MAX_QUEUE = 16  # Larger buffer for burst tolerance

async def zmq_reader(queue: asyncio.Queue):
    """Continuously read from ZMQ and enqueue frames, dropping half if full."""
    while True:
        data = await zmq_socket.recv()

        if queue.full():
            print(f"[WARN] Queue full ({queue.qsize()} frames). Dropping half...")

            # Drain the entire queue into a list
            drained = []
            while not queue.empty():
                try:
                    drained.append(queue.get_nowait())
                    queue.task_done()
                except asyncio.QueueEmpty:
                    break

            # Keep every 2nd frame
            kept = drained[::2]

            # Put back only the kept frames (synchronously, since we own the queue lock)
            for frame in kept:
                queue.put_nowait(frame)

        # Add the newest frame at the end
        await queue.put(data)


async def ws_sender(ws, queue: asyncio.Queue):
    """Continuously send frames from the queue to the WebSocket client."""
    try:
        while True:
            frame = await queue.get()
            await ws.send(frame)
            queue.task_done()
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def handler(ws):
    print("Client connected")

    # Make a larger queue for smoother handling
    queue = asyncio.Queue(maxsize=MAX_QUEUE)

    # Start a dedicated ZMQ reader
    zmq_task = asyncio.create_task(zmq_reader(queue))

    # Start sending frames
    await ws_sender(ws, queue)

    # Stop reader if client disconnects
    zmq_task.cancel()

async def main():
    print("[Vis] STARTING UP VISUALIZER", flush=True)
    async with websockets.serve(handler, "0.0.0.0", 8765, max_queue=1):
        await asyncio.Future()  # Keep server running

if __name__ == "__main__":
    asyncio.run(main())