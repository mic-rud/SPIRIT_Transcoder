import bitstream_bindings as bs
from bitstream import BitstreamIO

class Transcoder():
    def __init__(self, config):
        self.config = config
        self.bitstreamIO = BitstreamIO()

    def run(self):
        """
        Start a number of threads according to config
        """
        video_coder_threads = self.config["video_coder_threads"]


    def run_codec(self):
        pass