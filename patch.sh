HEADER="dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h"

FORWARD_DECLARATIONS=$(cat <<EOF
class SampleStreamV3CUnit;
class SEI;
class AtlasSequenceParameterSetRbsp;
class AtlasFrameParameterSetRbsp;
class AtlasTileLayerRbsp;
class VUIParameters;
class HrdSubLayerParameters;
class HrdParameters;
class MaxCodedVideoResolution;
class CoordinateSystemParameters;
class ProfileToolsetConstraintsInformation;
EOF
)

# Only insert if one of them is missing (using the first as a proxy)
if ! grep -q "class SampleStreamV3CUnit;" "$HEADER"; then
    sed -i '' "/namespace pcc {/a\\
$FORWARD_DECLARATIONS
" "$HEADER"
    echo "Inserted forward declarations into $HEADER"
else
    echo "Forward declarations already present in $HEADER"
fi
