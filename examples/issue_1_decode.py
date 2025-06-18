"""
Read bitstream -> Decode bitstream -> (modify) -> Encode bitstream -> Write back
"""
import bitstream_bindings as bs
import os
import numpy as np

def test():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input = os.path.join(base_dir, "test_data", "compressed", "S26C03R03.bin")
    output = os.path.join(base_dir, "test_data", "compressed", "S26C03R03_read_write.bin")

    print("Input path exists and is readable:", os.path.exists(input) & os.access(input, os.R_OK))

    bitstream = bs.PCCBitstream()
    ssvu = bs.PCCSampleStreamV3CUnit()
    reader = bs.PCCBitstreamReader()
    bitstreamStat_in = bs.PCCBitstreamStat()
    bitstreamStat_out = bs.PCCBitstreamStat()
    context = bs.PCCContext()
    writer = bs.PCCBitstreamWriter()
    output_bitstream = bs.PCCBitstream()
    new_ssvu = bs.PCCSampleStreamV3CUnit()


    ret = bitstream.initialize(input)
    if ret != 1:
        print("Error initialize")
        exit(1)


    headerSize = bs.PCCBitstreamReader.read(bitstream, ssvu)
    print("Bitstream HeaderSize: ",headerSize)

    bitstreamStat_in.setHeader(bitstream.size())
    bitstreamStat_in.incrHeader(headerSize)
    context.setBitstreamStat(bitstreamStat_in)


    ret = reader.decode(ssvu, context)
    if ret != 1:
        print("Error decode")
        exit(1)

    if context.checkProfile() != 0:
        print( "Profile not correct... \n" )
        exit(1)

    """
        Parameter manipulieren
    """
    # do to


    """
        Parameter in Syntax aktuallisieren
    """

    #header1 = syntax.getV3CUnitHeaderGVD().sequenceParamterSetId
    #print(header1)  # auf parameter direktzugreifen und printen
    #print(syntax.getV3CUnitHeaderAD())
    #print(syntax.getV3CUnitHeaderAVD())
    #print(syntax.getV3CUnitHeaderOVD())
    #print(syntax.getVps())
    #print(syntax.getAtlasSequenceParameterSet( 0 ))

    #syntax.setAtlasIndex(0)
    #syntax.addV3CParameterSet(0)
    #syntax.setActiveVpsId(0)

    atlas_count = context.getVps().getAtlasCountMinus1() + 1
    context.resizeAtlas(atlas_count)
    print("Atlas Count:",atlas_count)

    context.setAtlasIndex(0) # aktuell liegt nur 1 Atlas vor

    bitstreamStat_out.incrHeader(headerSize)
    bitstreamStat_out.setHeader(output_bitstream.size())
    context.setBitstreamStat( bitstreamStat_out )

    add_end_tile(context)

    """
        Daten aus Syntax in SSVU füllen und schreiben
    """
    ret = writer.encode(context, new_ssvu)
    if ret != 0:
        print("Error encode:", ret)
        exit(1)

    """
    new_context = bs.PCCContext()
    new_reader = bs.PCCBitstreamReader()
    new_bitstreamstat = bs.PCCBitstreamStat()

    #new_bitstreamstat.setHeader(0)
    new_bitstreamstat.incrHeader(headerSize)
    new_context.setBitstreamStat(new_bitstreamstat)

    ret = new_reader.decode(new_ssvu, new_context)   # das erneute decodieren zum Testen, alternativ über den PCCAppDecoder
    if ret != 1:
        print("Error decode")
        exit(1)

    exit(0)
    """
    writer.write_v3c(new_ssvu, output_bitstream)

    headerSize = output_bitstream.write(output)
    print("New Bitstream HeaderSize: ",headerSize)

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