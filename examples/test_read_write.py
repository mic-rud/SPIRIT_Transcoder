"""
Read bitstream -> Write bitstream
"""
import bitstream_bindings as bs
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

input_path = os.path.join(base_dir, "test_data", "compressed", "S26C03R03.bin")
output_path = os.path.join(base_dir, "test_data", "compressed", "S26C03R03_read_write.bin")

print("Input path exists and is readable:", os.path.exists(input_path) & os.access(input_path, os.R_OK))

# Initialize bitstream
bitstream_in = bs.PCCBitstream()
ret = bitstream_in.initialize(input_path)
if ret != 1:
    print("Error initialize")
    exit(1)

# Read bitstream
ssvu = bs.PCCSampleStreamV3CUnit()
headerSize = bs.PCCBitstreamReader.read(bitstream_in, ssvu)
print("Bitstream HeaderSize: ",headerSize)

# Write bitstream
bitstream_out = bs.PCCBitstream()
writer = bs.PCCBitstreamWriter()

writer.write_v3c(ssvu, bitstream_out)
bitstream_out.write(output_path)
print("Bitstream written to:", output_path)

# Compare input and output size
if bitstream_in.size() != bitstream_out.size():
    print("Error: Different size")
    exit(1)
