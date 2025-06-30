HEADER="/app/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h"

FORWARD_DECLARATIONS=$(cat <<EOF
class PCCBitstream;
class SampleStreamV3CUnit;
class SEI;
class AtlasSequenceParameterSetRbsp;
class AtlasFrameParameterSetRbsp;
class AtlasTileLayerRbsp;
class VUIParameters;
class HrdParameters;
class HrdSubLayerParameters;
class MaxCodedVideoResolution;
class CoordinateSystemParameters;
class ProfileToolsetConstraintsInformation;
EOF
)

awk -v insert="$FORWARD_DECLARATIONS" '
/namespace pcc {/ {
    print;
    print insert;
    next
}
1
' "$HEADER" > "$HEADER.patched" && mv "$HEADER.patched" "$HEADER"