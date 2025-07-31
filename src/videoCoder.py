import time
import av
import numpy as np
import io
import subprocess
import tempfile


class FFMPEGCoder:
    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        self.config = config

    def encode(self, frames: list[np.ndarray], config, video_type) -> bytes:
        if not frames:
            raise ValueError("No frames to encode.")

        h, w = config["height"], config["width"]
        if video_type == "occ":
            s = config["occ_prec"]
            h, w = h/s, w/s

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", config["pix_fmt"],
            "-s", f"{w}x{h}",
            "-r", str(config["fps"]),
            "-i", "-",
            "-c:v", config["codec"],
            "-preset", config["preset"],
            "-crf", config["crf"],
            "-f", "hevc", 
            "pipe:1"
        ] + self.config["extra_args"]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        for frame in frames:
            if frame.shape[:2] != (h, w):
                raise ValueError(f"Frame size mismatch. Expected ({h},{w}), got {frame.shape[:2]}")
            process.stdin.write(frame.astype(np.uint8).tobytes())

        process.stdin.close()
        encoded = process.stdout.read()
        process.wait()

        if process.returncode != 0:
            raise RuntimeError("FFmpeg encoding failed")

        return encoded
    

    def decode(self, video_bytes: bytes, config, video_type) -> list[np.ndarray]:
        t0 = time.time()
        cmd = [
            "ffmpeg",
            "-i", "pipe:0",
            "-f", "rawvideo",
            "-pix_fmt", config["pix_fmt"],
            "pipe:1"
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        out, _ = process.communicate(input=video_bytes)

        if process.returncode != 0:
            raise RuntimeError("FFmpeg decoding failed")

        t_dec = time.time() - t0
        print(f"Decoding {video_type}: {t_dec}s")

        h, w = config["height"], config["width"]
        if video_type == "occ":
            s = config["occ_prec"]
            h, w = h/s, w/s
        frame_size = h * w * 3

        n_frames = len(out) // frame_size
        frames = np.frombuffer(out, dtype=np.uint8).reshape((n_frames, h, w, 3))

        return list(frames)


class HEVCCoder:
    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        self.config = config

    def encode(self, frames: list[np.ndarray], config, video_type, pix_fmt) -> bytes:
        if not frames:
            raise ValueError("No frames to encode.")

        h, w = config["height"], config["width"]
        if video_type == "occ":
            pix_fmt = "gray"
            s = config["occ_prec"]
            h, w = h // s, w // s

        fps = config.get("fps", 30)
        crf = config.get("crf", "23")
        preset = config.get("preset", "medium")
        profile = config.get("profile", "main")
        threads = config.get("n_threads", 1)

        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=".hevc", delete=False) as f:
            tmp_path = f.name

        output = av.open(tmp_path, "w", format="hevc")
        codec_name = "libx265"

        stream = output.add_stream(codec_name, rate=fps)
        stream.width = w
        stream.height = h
        stream.pix_fmt = pix_fmt
        stream.options = {
            "crf": str(crf),
            "preset": preset,
            "profile": profile,
            "threads": str(threads),
        }

        if video_type == "occ":
            stream.options["x265-params"] = "lossless=1"

        for frame in frames:
            for packet in stream.encode(frame):
                output.mux(packet)

        # Flush last frame
        for packet in stream.encode():
            output.mux(packet)


        output.close()

        with open(tmp_path, "rb") as f:
            return f.read()

    def decode(self, video_bytes: bytes, config, video_type) -> list[np.ndarray]:
        t0 = time.time()
        if not isinstance(video_bytes, (bytes, bytearray)):
            raise TypeError("video_bytes must be bytes")

        h, w = config["height"], config["width"]
        if video_type == "occ":
            s = config["occ_prec"]
            h, w = h // s, w // s

        container = av.open(io.BytesIO(video_bytes), 
                            format="hevc", 
                            mode="r",
                            options={"threads": str(config["n_threads"])})

        frames = []
        for packet in container.demux(video=0):
            for frame in packet.decode():
                pix_fmt = frame.format.name
                frames.append(frame)

        # Flush delayed frames?

        print(f"Decoding {video_type}: {time.time() - t0:.3f}s")
        print(pix_fmt)
        print(len(frames))
        return frames, pix_fmt