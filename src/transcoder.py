import bitstream_bindings as bs
from bitstream import BitstreamIO
import threading
import time
import av
from videoCoder import HEVCVideoCoder


class Transcoder:
    def __init__(self, config):
        self.config = config
        self.bitstreamIO = BitstreamIO()
        self.hevc_coder = HEVCVideoCoder(config)

    def transcode(self, streams):
        """
        Start a number of threads according to config
        """
        t0 = time.time()

        for stream, stream_type in streams:
            codec_params = self.config.get("codec_params", {}).get(
                stream_type.name.lower(), {}
            )
            print("before substream: ", stream_type, ": ", len(stream.vector()))
            self.transcode_substream(stream, stream_type, codec_params)

        # just for tests
        for stream, stream_type in streams:
            print("after substream: ", stream_type, ": ", len(stream.vector()))

        print(f"Transcoding in {time.time() - t0:.2f}s")

    def transcode_substream(self, substream, stream_type, codec_params):
        sub_bytes = bytes(substream.vector())

        frames, pix_fmt = self.hevc_coder.transcode(sub_bytes)

        output_path = f"/app/data/tmp/transcoded_{stream_type.name.lower()}.hevc"

        encoded_bytes = self.hevc_coder.encode(
            frames,
            width=codec_params.get("width", frames[0].width),
            height=codec_params.get("height", frames[0].height),
            fps=codec_params.get("fps", 30),
            output_path=output_path,
            crf=codec_params.get("crf", 23),
            preset=codec_params.get("preset", "medium"),
            profile=codec_params.get("profile", "main10"),
            tier=codec_params.get("tier", "main"),
            rate_mode=codec_params.get("rate_mode", None),
            threads=self.config.get("num_video_coder_threads", 1),
            pix_fmt=pix_fmt,
        )

        substream.set_bytes(encoded_bytes)

    def run_codec(self):
        pass
