import bitstream_bindings as bs
from bitstream import BitstreamIO

class Transcoder():
    def __init__(self, config):
        self.config = config
        self.bitstreamIO = BitstreamIO()

    def transcode(self, path):
        """
        Start a number of threads according to config
        """
        t0 = time.time()
        context = self.bitstreamIO.read_bitstream(path), trace=True)
        
        num_video_coder_threads = self.config["num_video_coder_threads"]


    def transcode_substream(self, substream, stream_type, codec_params):
        substream.sampleStreamToByteStream()
        time.sleep()
        substream.byteStreamToSampleStream()
        


    def run_codec(self):
        pass