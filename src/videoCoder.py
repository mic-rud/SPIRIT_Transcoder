import av
import numpy as np

class HEVCVideoCoder():
    def __init__(self, configuration):
        self.configuration = configuration
    

    def update_config(self, config):
        pass

    def transcode(self, bytestream):
        container = av.open(bytestream, format='hevc', mode='r', buffer_size=len(bytestream))
        frames = []
        for packet in container.demux(video=0):
            for frame in packet.decode():
                frames.append(frame.to_ndarray(format='yuv10'))  # numpy array
        return frames

    def encode(self, frames, width, height, fps=30):
        output = av.open('output.hevc', 'w', format='hevc')
        stream = output.add_stream('libx265', rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'

        for frame_array in frames:
            frame = av.VideoFrame.from_ndarray(frame_array, format='yuv10')
            packet = stream.encode(frame)
            if packet:
                output.mux(packet)

        # Flush encoder
        for packet in stream.encode():
            output.mux(packet)

        output.close()
