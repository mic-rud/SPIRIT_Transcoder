"""
Read bitstream -> Decode bitstream -> Encode bitstream -> Write back
"""

import bitstream_bindings as bs
import numpy as np
import argparse
import subprocess
import os
import tempfile


def test():
    params = parse_parameters()

    """
        Initialize
    """
    bitstream_in = bs.PCCBitstream()
    bitstream_out = bs.PCCBitstream()
    ssvu_in = bs.PCCSampleStreamV3CUnit()
    ssvu_out = bs.PCCSampleStreamV3CUnit()
    bitstreamStat_in = bs.PCCBitstreamStat()
    bitstreamStat_out = bs.PCCBitstreamStat()

    ret = bitstream_in.initialize(params.compressedStreamPath)
    if ret != 1:
        print("Error initialize")
        exit(1)
    bitstreamStat_in.setHeader(bitstream_in.size())

    """
        Read bitstream
    """
    headerSize = bs.PCCBitstreamReader.read(bitstream_in, ssvu_in)
    print("Bitstream HeaderSize: ", headerSize)

    bitstreamStat_in.incrHeader(headerSize)
    bMoreData = True

    while bMoreData:
        context = bs.PCCContext()
        context.setBitstreamStat(bitstreamStat_in)
        reader = bs.PCCBitstreamReader()

        # Decode data
        ret = reader.decode(ssvu_in, context)
        if ret != 1:
            print("Error decode")
            exit(1)

        if context.checkProfile() != 0:
            print("Profile not correct... \n")
            exit(1)

        # Add parameters for encoding
        context.resizeAtlas(context.getVps().getAtlasCountMinus1() + 1)

        for atlId in range(context.getVps().getAtlasCountMinus1() + 1):
            context.setAtlasIndex(atlId)
            transcodeData(context, params)
            add_end_tile(context)  # add missing byte add the end of last patch

            # Encode data
            context.setBitstreamStat(bitstreamStat_out)
            writer = bs.PCCBitstreamWriter()
            ret = writer.encode(context, ssvu_out)
            if ret != 0:
                print("Error encode:", ret)
                exit(1)

            bMoreData = ssvu_in.getV3CUnitCount() > 0

    # Write data to bitstream
    writer = bs.PCCBitstreamWriter()
    bitstreamStat_out.setHeader(bitstream_out.size())
    writer.write_v3c(ssvu_out, bitstream_out, params.forcedSsvhUnitSizePrecisionBytes)
    bitstreamStat_out.incrHeader(headerSize)
    bitstream_out.write(params.outStreamPath)
    print("Bitstream written to:", params.outStreamPath)

    print("################IN################")
    bitstreamStat_in.trace(False)
    print("################OUT###############")
    bitstreamStat_out.trace(False)


def add_end_tile(context):
    atglus = context.getAtlasTileLayerList()
    for atglu in atglus:
        ath = atglu.getHeader()
        atgdu = atglu.getDataUnit()
        patchType = (
            bs.PCCPatchModeITile.I_END
            if ath.getType() == bs.PCCTileType.I_TILE
            else bs.PCCPatchModePTile.P_END
        )
        atgdu.addPatchInformationData(np.uint8(patchType))


def transcodeData(context, params):
    if False:
        # transcodeBaseline(context) # not used
        return 0
    else:
        # Transcode Occupancy video
        if params.occupancyPrecision == 4:
            occVideoBitstream = context.getVideoBitstream(
                bs.PCCVideoType.VIDEO_OCCUPANCY
            )
            occVideoBitstream.sampleStreamToByteStream()
            transcodeVideo(occVideoBitstream, bs.PCCVideoType.VIDEO_OCCUPANCY, params)
            context.setOccupancyPrecision(params.occupancyPrecision)
            occVideoBitstream.byteStreamToSampleStream()

        # Transcode Geometry video
        geoVideoBitstream = context.getVideoBitstream(bs.PCCVideoType.VIDEO_GEOMETRY)
        geoVideoBitstream.sampleStreamToByteStream()
        transcodeVideo(geoVideoBitstream, bs.PCCVideoType.VIDEO_GEOMETRY, params)
        geoVideoBitstream.byteStreamToSampleStream()

        # Transcode Attribute video
        attVideoBitstream = context.getVideoBitstream(bs.PCCVideoType.VIDEO_ATTRIBUTE)
        attVideoBitstream.sampleStreamToByteStream()
        transcodeVideo(attVideoBitstream, bs.PCCVideoType.VIDEO_ATTRIBUTE, params)
        attVideoBitstream.byteStreamToSampleStream()

def transcodeVideo(videoBitstream, type, params):
    input_bytes = bytes(videoBitstream.vector())
    
    output_bytes = input_bytes
    
    vec = videoBitstream.vector()
    vec.clear()
    vec.extend(output_bytes)


def parse_parameters():
    parser = argparse.ArgumentParser()

    parser.add_argument("--Threads", type=int, dest="nbThread", default=1)
    parser.add_argument("--outStreamPath", type=str, dest="outStreamPath")
    parser.add_argument(
        "--forcedSsvhUnitSizePrecisionBytes",
        type=int,
        dest="forcedSsvhUnitSizePrecisionBytes",
        default=0,
    )
    parser.add_argument(
        "--occupancyPrecision", type=int, dest="occupancyPrecision", default=4
    )
    parser.add_argument("--compressedStreamPath", type=str, dest="compressedStreamPath")

    args = parser.parse_args()

    params = Parameter()
    params.nbThread = args.nbThread
    params.outStreamPath = args.outStreamPath
    params.forcedSsvhUnitSizePrecisionBytes = args.forcedSsvhUnitSizePrecisionBytes
    params.occupancyPrecision = args.occupancyPrecision
    params.compressedStreamPath = args.compressedStreamPath

    return params


class Parameter:
    def __init__(self):
        self.nbThread = 1
        self.outStreamPath = None
        self.forcedSsvhUnitSizePrecisionBytes = 0
        self.occupancyPrecision = 4
        self.compressedStreamPath = None


if __name__ == "__main__":
    test()