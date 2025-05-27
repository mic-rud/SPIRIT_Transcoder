"""
Implements the bitstream wrapping in python to read a V3C bitstream
"""
import bitstream_bindings

#First test, if importing works, without linking errors
bitstream = bitstream_bindings.PCCBitstream()
reader = bitstream_bindings.PCCBitstreamReader()
writer = bitstream_bindings.PCCBitstreamWriter()

print(bitstream.size())
