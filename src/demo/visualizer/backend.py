import time
import asyncio
import websockets
import yaml
import zmq
import zmq.asyncio

# Initialize ZeroMQ context and socket (PULL for receiving data)
context = zmq.asyncio.Context()
zmq_socket = context.socket(zmq.PULL)
zmq_socket.bind("tcp://*:5556")  # Connect to the ZeroMQ source

async def handler(websocket):
    print("Client connected")
    try:
        while True:
            start_time = time.time()
            # Wait for message
            data = await zmq_socket.recv()
            
            # Send  data to WebSocket client
            asyncio.create_task(websocket.send(data))  
            done_time = time.time()
            print("[Vis] RUNNING in {} s".format(done_time - start_time), flush=True)

    except websocket.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    print("[Vis] STARTING UP VISUALIZER", flush=True)
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # Keep the server running

# Run the WebSocket server
asyncio.run(main())