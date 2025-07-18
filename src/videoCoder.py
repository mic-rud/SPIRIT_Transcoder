import av
import numpy as np
import io


class HEVCVideoCoder:
    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        pass

    def transcode(self, bytestream):
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
