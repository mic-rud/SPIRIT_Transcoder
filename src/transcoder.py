import bitstream_bindings as bs
from bitstream import BitstreamIO
from concurrent.futures import ThreadPoolExecutor
import time
from videoCoder import HEVCCoder, FFMPEGCoder

class Transcoder:
    def __init__(self, config):
        self.bitstreamIO = BitstreamIO()
        #self.video_coder = FFMPEGCoder(config)
        self.video_coder = HEVCCoder(config)

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
            #"occ": context.getVideoBitstream(bs.PCCVideoType.VIDEO_OCCUPANCY),
            "geo": context.getVideoBitstream(bs.PCCVideoType.VIDEO_GEOMETRY),
            "att": context.getVideoBitstream(bs.PCCVideoType.VIDEO_ATTRIBUTE),
        }

        # Extract Deocding information
        asps = context.getAtlasSequenceParameterSet(0)
        config["height"] = asps.getFrameHeight()
        config["width"] = asps.getFrameWidth()

        # Transcode all streams in parallel (decode + encode)
        futures = {
            key: self.workers.submit(
                self.transcode_substream,
                byte_stream,
                key,
                config
            )
            for key, byte_stream in video_streams.items()
        }

        # Collect encoded results and patch back into context
        for f in futures.values():
            f.result()

        # Write the data again
        self.bitstreamIO.write_bitstream(context, config["out_path"], trace=True)
        return 

    def transcode_substream(self, substream, video_type, config):
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
        decoded_frames, pix_fmt = self.video_coder.decode(bytestream, config["decode"], video_type)
        encoded_bytes = self.video_coder.encode(decoded_frames, config["encode"], video_type, pix_fmt)

        # Set encoded bytes to substream
        substream.set_bytes(encoded_bytes)
        substream.byteStreamToSampleStream()
        return 
        