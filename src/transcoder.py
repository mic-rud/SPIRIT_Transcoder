import bitsteam_bindings as bs
from bitstream import BitstreamIO
import concurrent.futures as ThreadPoolExecutor
import time
from videoCoder import HEVCVideoCoder, FFMPEGCoder

class Transcoder:
    def __init__(self, config):
        self.bitstreamIO = BitstreamIO()
        self.video_coder = FFMPEGCoder(config)

        self.workers = ThreadPoolExecutor(max_workers=3)

    def transcode(self, in_stream, out_stream, config):
        """
        Transcode an input stream (path or buffer according to the configuration)
        Paramters:
            in_stream (str): Path to the origin stream
            out_stream (str): Path to the transcoded stream
            config (dict): Dictionary containing the transcoding configuration
        """
        # Load and Parse Bitstream
        if type(in_stream) is str:
            context = self.bitstreamIO.read_bitstream(config["in_path"], trace=True)
        else: 
            raise TypeError("Parsing from memory not yet implemented")

         # Extract and convert video substreams to byte streams
        video_streams = {
            "occ": bytes(context.getVideoBitstream(bs.PCCVideoType.VIDEO_OCCUPANCY)),
            "geo": bytes(context.getVideoBitstream(bs.PCCVideoType.VIDEO_GEOMETRY)),
            "att": bytes(context.getVideoBitstream(bs.PCCVideoType.VIDEO_ATTRIBUTE)),
        }

        # Transcode all streams in parallel (decode + encode)
        futures = {
            key: self.executor.submit(
                self.transcode_substream,
                byte_stream,
                config[key]
            )
            for key, byte_stream in video_streams.items()
        }

        # Collect encoded results and patch back into context
        for f in futures.values():
            f.result()

        # Write the data again
        self.bitstreamIO.write_bitstream(context, config["out_path"], trace=True)
        return 

    def transcode_substream(self, substream, config):
        """
        Transcode a substream according to the given config.

        Parameters:
            substream : Reference to the Video substream
            config (dict): Dictionary containing the encoding and 
                           decoding configuration for the substream
        """
        
        # Extract Bytes from substream
        substream.sampleStreamToByteStream()
        bytestream = bytes(substream.vector())

        # Decode and encode acording to the config
        decoded_frames = self.video_coder.decode(bytestream, config["decode"])
        encoded_bytes = self.video_coder.encode(decoded_frames, config["encode"])

        # Set encoded bytes to substream
        substream.set_bytes(encoded_bytes)
        substream.byteStreamToSampleStream()
        return 
        


        

    def transcode2(self, streams):
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
