import bitstream_bindings as bs
from utils.bitstream import BitstreamIO
from concurrent.futures import ProcessPoolExecutor
import time
from transcoder.videoCoder import HEVCCoder, FFMPEGCodec
def transcode_bytes(bytestream, config, video_type):
    coder = FFMPEGCodec()
    coder.init_codec(config, video_type)
    return coder.transcode(bytestream, config, video_type)


class Transcoder:
    def __init__(self, config):
        #self.video_coder = HEVCCoder(config)
        self.bitstreamIO = BitstreamIO()
        self.workers = ProcessPoolExecutor(max_workers=2)

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
            context = self.bitstreamIO.read_bitstream(in_stream, trace=False)
        else: 
            raise TypeError("Parsing from memory not yet implemented")

        # Extract and convert video substreams to byte streams
        video_streams = {
            #"occ": context.getVideoBitstream(bs.PCCVideoType.VIDEO_OCCUPANCY),
            "geo": context.getVideoBitstream(bs.PCCVideoType.VIDEO_GEOMETRY),
            "att": context.getVideoBitstream(bs.PCCVideoType.VIDEO_ATTRIBUTE),
        }

        # Extract Deocding information
        asps = context.getAtlasSequenceParameterSet(0)
        config["height"] = asps.getFrameHeight()
        config["width"] = asps.getFrameWidth()

        # Convert substreams to bytes
        stream_bytes = {}
        for key, substream in video_streams.items():
            substream.sampleStreamToByteStream()
            stream_bytes[key] = bytes(substream.vector())

        # Submit jobs
        futures = {
            key: self.workers.submit(transcode_bytes, stream_bytes[key], config, key)
            for key in stream_bytes
        }

        # Collect results and re-encode substreams
        for key, future in futures.items():
            encoded = future.result()

            size_ratio = len(stream_bytes[key]) / len(encoded)
            print("{}: RATE RATO: {}".format(key, size_ratio))
            video_streams[key].set_bytes(encoded)
            video_streams[key].byteStreamToSampleStream()

        # Write the data again
        self.bitstreamIO.write_bitstream(context, out_stream, trace=False)
        return 