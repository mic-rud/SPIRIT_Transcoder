import av
import numpy as np
import io

class HEVCVideoCoder():
    def __init__(self, configuration):
        self.configuration = configuration
    

    def update_config(self, config):
        pass

    def transcode(self, bytestream):
        if isinstance(bytestream, bytes):
            buffer_size = len(bytestream)
            bytestream = io.BytesIO(bytestream)
        container = av.open(bytestream, format='hevc', mode='r', buffer_size=buffer_size)
        frames = []
        for packet in container.demux(video=0):
            for frame in packet.decode():
                frames.append(frame.to_ndarray(format='yuv420p'))  # numpy array
        return frames

    def encode(self, frames, width, height, fps=30, output_path=''):
        output = av.open(output_path, 'w', format='hevc')
        stream = output.add_stream('libx265', rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'

        for frame_array in frames:
            frame = av.VideoFrame.from_ndarray(frame_array, format='yuv420p')
            packet = stream.encode(frame)
            if packet:
                output.mux(packet)

        # Flush encoder
        for packet in stream.encode():
            output.mux(packet)

        output.close()
