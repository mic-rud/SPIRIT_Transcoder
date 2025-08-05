from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import os, threading, queue, subprocess

app = FastAPI()
MEDIA_DIR = "/path/to/project/media"
SOURCE_DIR = "/path/to/project/source"

segment_status = {}
segment_lock = threading.Lock()
transcode_queue = queue.Queue()

@app.get("/{path:path}")
def handle_request(path: str):
    full_path = os.path.join(MEDIA_DIR, path)

    if os.path.exists(full_path):
        return FileResponse(full_path)

    rep_id, seg_num = parse_segment(path)
    key = f"{rep_id}_{seg_num}"

    with segment_lock:
        status = segment_status.get(key, "missing")

        if status == "queued":
            raise HTTPException(status_code=503, detail="Segment queued")
        elif status == "available" and os.path.exists(full_path):
            return FileResponse(full_path)
        else:
            segment_status[key] = "queued"
            transcode_queue.put((rep_id, seg_num, path))
            raise HTTPException(status_code=503, detail="Segment queued")

def parse_segment(name: str):
    try:
        parts = name.split("-")
        rep = parts[1]
        seg = int(parts[2].split(".")[0])
        return rep, seg
    except Exception:
        raise HTTPException(status_code=404, detail="Bad segment name")

def transcode_worker():
    while True:
        rep_id, seg_num, rel_path = transcode_queue.get()
        key = f"{rep_id}_{seg_num}"
        out_path = os.path.join(MEDIA_DIR, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        # Transcode here!

        with segment_lock:
            segment_status[key] = "available" if success else "error"

threading.Thread(target=transcode_worker, daemon=True).start()
