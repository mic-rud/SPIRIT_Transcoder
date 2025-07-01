import numpy as np
import bitstream_bindings as bs

class BitstreamIO():
    def __init__(self):
        self.bitstream_reader = bs.PCCBitstreamReader()
        self.bitstream_writer = bs.PCCBitstreamWriter()


    def read_bitstream(self, path, trace=False):
        """
        Reads a bitstream from the specified path.

        args:
            path (str): Path to the bitstream
        
        returns:
            context (PCCContext): Context object of the decoded bitstream
        """
        ssvu = bs.PCCSampleStreamV3CUnit()
        context = bs.PCCContext()
        bitstream = bs.PCCBitstream()
        bitstream_stat = bs.PCCBitstreamStat()

        # Read the bitstream
        ret = bitstream.initialize(path)
        if ret != 1:
            raise ValueError("Error initialize")

        # Setup Header
        
        # TODO: Commented out and the parsing seems to work ?
        headerSize = self.bitstream_reader.read(bitstream, ssvu)
        bitstream_stat.setHeader(bitstream.size())
        #bitstream_stat.incrHeader(headerSize)

        context.setBitstreamStat(bitstream_stat)

        # Decode and check correctness
        ret = self.bitstream_reader.decode(ssvu, context)
        if ret != 1:
            raise ValueError("Error during bitstream decoding")
        if context.checkProfile() != 0:
            raise ValueError("Error: Profile not correct.")

        context.setBitstreamStat(bitstream_stat)

        # Set End tile: Move to writing?
        self.add_end_tile(context)
        if trace:
            print("################# IN BITSTREAM #################")
            bitstream_stat.trace(False)

        return context


    def add_end_tile(self, context):
        atglus = context.getAtlasTileLayerList()
        for atglu in atglus:
            ath = atglu.getHeader()
            atgdu = atglu.getDataUnit()
            patchType = bs.PCCPatchModeITile.I_END if ath.getType() == bs.PCCTileType.I_TILE else bs.PCCPatchModePTile.P_END
            atgdu.addPatchInformationData(np.uint8(patchType))


    def write_bitstream(self, context, path, trace=False):
        """
        Write a bitstream to the specified path.

        args:
            path (str): Path to the bitstream
            context (PCCContext): Context object of the decoded bitstream
        """
        ssvu = bs.PCCSampleStreamV3CUnit()
        bitstream = bs.PCCBitstream()
        bitstream_stat = bs.PCCBitstreamStat()

        bitstream_stat.setHeader(bitstream.size())
        context.setBitstreamStat(bitstream_stat)

        # Encode the context
        ret = self.bitstream_writer.encode(context, ssvu)
        if ret != 0:
            raise ValueError("Error: Failed to encode context to SSVU")

        # Write data 
        self.bitstream_writer.write_v3c(ssvu, bitstream)
        bitstream.write(path)

        if trace:
            print("################# OUT BITSTREAM #################")
            #bitstream_stat.trace(False)