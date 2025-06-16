"""
Read bitstream -> Decode bitstream -> (modify) -> Encode bitstream -> Write back
"""
import bitstream_bindings as bs
import os

#to do
#change path to relative
input="/home/fschnier/Dokumente/Studium/Master/Hiwi-Job/SPIRIT-pyRABBIT/examples/test_data/compressed/S26C03R03.bin"
output="/home/fschnier/Dokumente/Studium/Master/Hiwi-Job/SPIRIT-pyRABBIT/examples/test_data/compressed/S26C03R03_edited.bin"

print("Input path exists and is readable:", os.path.exists(input) & os.access(input, os.R_OK))

bitstream = bs.PCCBitstream()
ssvu = bs.PCCSampleStreamV3CUnit()
reader = bs.PCCBitstreamReader()
bitstreamstat = bs.PCCBitstreamStat()
syntax = bs.PCCHighLevelSyntax()
writer = bs.PCCBitstreamWriter()
output_bitstream = bs.PCCBitstream()
new_ssvu = bs.PCCSampleStreamV3CUnit()


ret = bitstream.initialize(input)
if ret != 1:
    print("Error initialize")
    exit(1)


headerSize = bs.PCCBitstreamReader.read(bitstream, ssvu)
print("Bitstream HeaderSize: ",headerSize)

bitstreamstat.setHeader(bitstream.size())
bitstreamstat.incrHeader(headerSize)
syntax.setBitstreamStat(bitstreamstat)

ret = reader.decode(ssvu, syntax)
if ret != 1:
    print("Error decode")
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

#tmpstat = bs.PCCBitstreamStat()

#syntax.setBitstreamStat(tmpstat)

#syntax.setAtlasIndex(0)
#syntax.addV3CParameterSet(0)
#syntax.setActiveVpsId(0)


"""
    Daten aus Syntax in SSVU füllen und schreiben
"""
ret = writer.encode(syntax, new_ssvu)
if ret != 0:
    print("Error encode:", ret)
    exit(1)

new_syntax = bs.PCCHighLevelSyntax()
new_reader = bs.PCCBitstreamReader()
new_bitstreamstat = bs.PCCBitstreamStat()

#new_bitstreamstat.setHeader(0)
#new_bitstreamstat.incrHeader(headerSize)
new_syntax.setBitstreamStat(new_bitstreamstat)

ret = new_reader.decode(new_ssvu, new_syntax)   # das erneute decodieren zum Testen, alternativ über den PCCAppDecoder
if ret != 1:
    print("Error decode")
    exit(1)

exit(0)


headerSize = output_bitstream.write(output)
print("New Bitstream HeaderSize: ",headerSize)

print("Bitstream written to:", output)
