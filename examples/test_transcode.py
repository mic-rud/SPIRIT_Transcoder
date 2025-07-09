"""
Read bitstream -> Decode bitstream -> Encode bitstream -> Write back
"""
import bitstream_bindings as bs
import os
import numpy as np

def test():
    base_dir    = os.path.dirname(os.path.abspath(__file__))
    input       = os.path.join(base_dir, "test_data", "compressed", "S26C03R03_30frames.bin")
    output      = os.path.join(base_dir, "test_data", "compressed", "S26C03R03_transcode.bin")
    print("Input path exists and is readable:", os.path.exists(input) & os.access(input, os.R_OK))

    """
        Initialize
    """
    bitstream_in        = bs.PCCBitstream()
    bitstream_out       = bs.PCCBitstream()
    ssvu_in             = bs.PCCSampleStreamV3CUnit()
    ssvu_out            = bs.PCCSampleStreamV3CUnit()
    bitstreamStat_in    = bs.PCCBitstreamStat()
    bitstreamStat_out   = bs.PCCBitstreamStat()

    
    ret = bitstream_in.initialize(input)
    if ret != 1:
        print("Error initialize")
        exit(1)

    """
        Read bitstream
    """
    headerSize = bs.PCCBitstreamReader.read(bitstream_in, ssvu_in)
    print("Bitstream HeaderSize: ",headerSize)


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
            print( "Profile not correct... \n" )
            exit(1)


        # Add parameters for encoding
        context.resizeAtlas( context.getVps().getAtlasCountMinus1() + 1 )
        
        for atlId in range(context.getVps().getAtlasCountMinus1() + 1):
            context.setAtlasIndex( atlId )
            #transcodeData(context) to do for next step
            add_end_tile(context) # add missing byte add the end of last patch

            # Encode data
            context.setBitstreamStat( bitstreamStat_out );
            writer = bs.PCCBitstreamWriter()
            ret = writer.encode(context, ssvu_out)
            if ret != 0:
                print("Error encode:", ret)
                exit(1)
                
            bMoreData = ( ssvu_in.getV3CUnitCount() > 0 )
        

    # Write data to bitstream
    writer = bs.PCCBitstreamWriter()
    bitstreamStat_out.setHeader(bitstream_out.size())
    writer.write_v3c(ssvu_out, bitstream_out)
    bitstreamStat_out.incrHeader( headerSize )
    bitstream_out.write(output)
    print("Bitstream written to:", output)
    
    

    print("################IN################")
    bitstreamStat_in.trace(False)
    print("################OUT###############")
    bitstreamStat_out.trace(False)

def add_end_tile(context):

    atglus = context.getAtlasTileLayerList()
    for atglu in atglus:
        ath = atglu.getHeader()
        atgdu = atglu.getDataUnit()
        patchType = bs.PCCPatchModeITile.I_END if ath.getType() == bs.PCCTileType.I_TILE else bs.PCCPatchModePTile.P_END
        atgdu.addPatchInformationData(np.uint8(patchType))

if __name__ == "__main__":
    test()