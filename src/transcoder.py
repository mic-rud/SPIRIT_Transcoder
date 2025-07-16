import bitstream_bindings as bs
from bitstream import BitstreamIO
import threading
import time
import av
from videoCoder import HEVCVideoCoder


class Transcoder():
    def __init__(self, config):
        self.config = config
        self.bitstreamIO = BitstreamIO()
        self.hevc_coder = HEVCVideoCoder(config)

    def transcode(self, streams):
        """
        Start a number of threads according to config
        """
        t0 = time.time()
        threads = []
        for stream, stream_type in streams:
            codec_params = self.config.get("codec_params", {}).get(stream_type.name.lower(), {})
            print("before substream: ",stream_type, ": ", len(stream.vector()))
            self.transcode_substream(stream, stream_type, codec_params)
            #t = threading.Thread(target=self.transcode_substream, args=(stream, stream_type, codec_params))
            #t.start()
            #threads.append(t)
            
        #for t in threads:
        #    print("after substream: ",stream_type, ": ", len(stream.vector()))
        #    t.join()
        for stream, stream_type in streams:
            print("after substream: ",stream_type, ": ", len(stream.vector()))
        
        print(f"Transcoding in {time.time() - t0:.2f}s")

    def transcode_substream(self, substream, stream_type, codec_params):
        
        sub_bytes = bytes(substream.vector())
        
        frames = self.hevc_coder.transcode(sub_bytes)
        
        output_path = f"/app/data/tmp/transcoded_{stream_type.name.lower()}.hevc"

        self.hevc_coder.encode(
            frames,
            width = codec_params.get("width", frames[0].shape[1]),
            height = codec_params.get("width", frames[0].shape[0]),
            fps = codec_params.get("fps", 30),
            output_path = output_path
        )
        
        with open(output_path, "rb") as f:
            encoded_bytes = f.read()
            
        substream.set_bytes(encoded_bytes)

    def run_codec(self):
        pass