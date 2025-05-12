HEADER="dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h"

FORWARD_DECLARATION="class SampleStreamV3CUnit;\\class SEI;\\classAtlasSequenceParameterSetRbsp;"

if ! grep -q "$FORWARD_DECLARATION" "$HEADER"; then
    sed -i '' "/namespace pcc {/a\\
$FORWARD_DECLARATION
" "$HEADER"
    echo "Inserted: $FORWARD_DECLARATION"
else
    echo "Already declared: $FORWARD_DECLARATION"
fi
