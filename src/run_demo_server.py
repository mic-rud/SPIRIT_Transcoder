import yaml
import uvicorn

from transcoder.transcoder import Transcoder
from demo.server import TranscodingService, WSCommand

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

config_path = "/app/configs/demo_config.yaml"
media_dir = "/app/data/encoded/demo_vox9"
processed_dir = "/app/data/processed"
num_segments = 40
segment_duration = 1.0
default_config = {
    "key": 0
}

app = FastAPI()
worker = Transcoder(default_config)

with open(config_path, "r") as f:
    base_config = yaml.safe_load(f)
rate_config_path = base_config.get("rate-config", "rate/R1.yaml")
with open(rate_config_path, "r") as f:
    rate_config = yaml.safe_load(f)

base_config.update(rate_config)

initial_config = {
    "sequence": "longdress",
    "coding_config": base_config, 
}

manager = TranscodingService(
    worker=worker,
    media_dir=media_dir, 
    processed_dir=processed_dir, 
    num_segments=num_segments,
    segment_duration=segment_duration)
manager.update_config(initial_config)

@app.websocket("/ws")
async def websocket_handler(ws: WebSocket):
    await ws.accept()
    manager.client = ws
    push_task = asyncio.create_task(manager.start_loop())

    try:
        while True:
            print("[Server] Awaiting client messages")
            data = await ws.receive_json()

            msg = WSCommand(**data)
            if msg.type == "AdjustConfig" and msg.coding_config:
                manager.update_config(coding_config=msg)
                await ws.send_json({"type": "Ack"})
            else:
                await ws.send_json({"type": "Err", "reason": "Invalid control mesage"})

    except WebSocketDisconnect:
        print("[Server] Stopping server")
        manager.stop()
        push_task.cancel()


if __name__ == "__main__":
    uvicorn.run("run_demo_server:app", host="0.0.0.0", port=8000, reload=False)
