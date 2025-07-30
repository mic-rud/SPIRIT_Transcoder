import av
import numpy as np
import io
import subprocess
from dataclass import dataclass
from typing import Optional


class FFMPEGCoder:
    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        self.config = config

    def encode(self, frames: list[np.ndarray]) -> bytes:
        if not frames:
            raise ValueError("No frames to encode.")

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", self.config["pix_fmt"],
            "-s", f"{self.config["width"]}x{self.config["height"]}",
            "-r", str(self.config["fps"]),
            "-i", "-",
            "-c:v", self.config["codec"],
            "-preset", self.config["preset"],
            "-crf", self.config["crf"],
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
            if frame.shape[:2] != (self.config["height"], self.config["width"]):
                raise ValueError(f"Frame size mismatch. Expected ({self.config["height"]},{self.config["width"]}), got {frame.shape[:2]}")
            process.stdin.write(frame.astype(np.uint8).tobytes())

        process.stdin.close()
        encoded = process.stdout.read()
        process.wait()

        if process.returncode != 0:
            raise RuntimeError("FFmpeg encoding failed")

        return encoded
    

    def decode(self, video_bytes: bytes) -> list[np.ndarray]:
        cmd = [
            "ffmpeg",
            "-i", "pipe:0",
            "-f", "rawvideo",
            "-pix_fmt", self.config["pix_fmt"],
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

        frame_size = self.config["height"] * self.config["width"]
        n_frames = len(out) // frame_size
        frames = np.frombuffer(out, dtype=np.uint8).reshape((n_frames, self.height, self.width, 3))
        return list(frames)


class HEVCVideoCoder:
    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        pass

    def decode(self, bytestream):
        if isinstance(bytestream, bytes):
            buffer_size = len(bytestream)
            bytestream = io.BytesIO(bytestream)
        container = av.open(
            bytestream, format="hevc", mode="r", buffer_size=buffer_size
        )
        frames = []
        pix_fmt = None
        for packet in container.demux(video=0):
            for frame in packet.decode():
                if pix_fmt is None:
                    pix_fmt = frame.format.name
                frames.append(frame)
        if pix_fmt is None:
            pix_fmt = "yuv420p"
        return frames, pix_fmt

    def encode(
        self,
        frames,
        width,
        height,
        fps=30,
        output_path="",
        crf="23",
        preset="medium",
        profile="main",
        tier="main",
        rate_mode=None,
        threads=1,
        pix_fmt="yuv420p",
    ):
        output = av.open(output_path, "w", format="hevc")
        codec_name = "libx265"

        if self.config.get("useCuda", False):
            codec_name = "hevc_nvenc"

        stream = output.add_stream(codec_name, rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = pix_fmt

        stream.options = {
            "crf": str(crf),
            "preset": preset,
            "profile": profile,
            "threads": str(threads),
        }

        if rate_mode:
            stream.options["x265-params"] = rate_mode
            
        for frame in frames:
            packet = stream.encode(frame)
            if packet:
                output.mux(packet)
        
        for packet in stream.encode():
            output.mux(packet)

        output.close()
        with open(output_path, "rb") as f:
            return f.read()
