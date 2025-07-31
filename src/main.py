import time
import yaml
from transcoder import Transcoder
import bitstream_bindings as bs
from bitstream import BitstreamIO

def transcode(config_path):
    # Load config
    print(config_path)
    with open (config_path, "r") as f:
        config = yaml.safe_load(f)

    t0 = time.time()

    #bitstream_parser= BitstreamIO()
    ## Read the bitstream
    #context = bitstream_parser.read_bitstream(config["in_path"], trace=True)

    ## Extract video substreams 
    #occVideoBitstream = context.getVideoBitstream(bs.PCCVideoType.VIDEO_OCCUPANCY)
    #geoVideoBitstream = context.getVideoBitstream(bs.PCCVideoType.VIDEO_GEOMETRY)
    #attVideoBitstream = context.getVideoBitstream(bs.PCCVideoType.VIDEO_ATTRIBUTE)

    ## To bytestream
    #occVideoBitstream.sampleStreamToByteStream()
    #geoVideoBitstream.sampleStreamToByteStream()
    #attVideoBitstream.sampleStreamToByteStream()

    ##transcode_video(occVideoBitstream, bs.PCCVideoType.VIDEO_OCCUPANCY)
    ##transcode_video(geoVideoBitstream, bs.PCCVideoType.VIDEO_GEOMETRY, params)
    ##transcode_video(attVideoBitstream, bs.PCCVideoType.VIDEO_ATTRIBUTE)
    #streams = [
            #(occVideoBitstream, bs.PCCVideoType.VIDEO_OCCUPANCY),
            #(geoVideoBitstream,  bs.PCCVideoType.VIDEO_GEOMETRY),
            #(attVideoBitstream, bs.PCCVideoType.VIDEO_ATTRIBUTE)
        #]
    #occVideoBitstream.byteStreamToSampleStream()
    #geoVideoBitstream.byteStreamToSampleStream()
    #attVideoBitstream.byteStreamToSampleStream()


    #bitstream_parser.write_bitstream(context, config["out_path"], trace=True)
    
    transcoder = Transcoder(config)
    transcoder.transcode(config["in_path"], config["out_path"], config)


    print("Total time: {}".format(time.time() - t0))




if __name__ == "__main__":
    config_path = "/app/configs/test_config.yaml"
    transcode(config_path)