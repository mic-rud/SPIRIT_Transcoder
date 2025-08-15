#!/bin/bash

# Check argument
if [ $# -lt 3 ]; then
  echo "Usage: $0 <gop_size> <data_base> <out_dir>"
  exit 1
fi

# Arguments
GOP_SIZE="$1"
DATA_BASE="$2"
OUT_DIR="$3"

TOTAL_FRAMES=600
NUM_SEGMENTS=$((TOTAL_FRAMES / GOP_SIZE))

# Base paths
TMC2_BIN="/app/dependencies/mpeg-pcc-tmc2/bin/PccAppEncoder"
CFG_BASE="/app/dependencies/mpeg-pcc-tmc2/cfg"

# Arrays for input sequences and their start frames
declare -A START_FRAMES=(
  [redandblack]=1450
  [longdress]=1051
  [soldier]=536
  [loot]=1000
)

# Extend sequence to 600 frames in-place
for INFILE in "${!START_FRAMES[@]}"; do
  START_FRAME="${START_FRAMES[$INFILE]}"
  SRC_DIR="${DATA_BASE}/${INFILE}"

  # Append reversed frames: 299 to 0
  for ((i=299; i>=0; i--)); do
    SRC_FRAME=$(printf "%04d" $((START_FRAME + i)))
    DST_FRAME=$(printf "%04d" $((START_FRAME + 300 + (299 - i)))
)
    cp "${SRC_DIR}/${INFILE}_vox10_${SRC_FRAME}.ply" \
       "${SRC_DIR}/${INFILE}_vox10_${DST_FRAME}.ply"
  done

  echo "Extended $INFILE to 600 frames starting at $START_FRAME"
done

echo "Converting 'double' to 'float' in PLY headers..."
find "$DATA_BASE" -type f -name "*.ply" -print0 | while IFS= read -r -d '' file; do
  # Backup is optional, uncomment if needed:
  # cp "$file" "$file.bak"
  sed -i 's/\<double\>/float/g' "$file"
done


# Encoding settings
CFG_COMMON="$CFG_BASE/common/ctc-common.cfg"
CFG_CONDITION="$CFG_BASE/condition/ctc-all-intra.cfg"
CFG_RATE="$CFG_BASE/rate/ctc-r5.cfg"

mkdir -p "$OUT_DIR"

# Loop through all sequences
for INFILE in "${!START_FRAMES[@]}"; do
  START_FRAME="${START_FRAMES[$INFILE]}"
  SEQ_CFG="/app/configs/tmc2_configs/${INFILE}_vox9.cfg"
  
  PLY_INPUT="${DATA_BASE}/${INFILE}/${INFILE}_vox10_%04d.ply"
  RECON_OUT="${INFILE}_rec_%04d.ply"

  for ((PART=0; PART<NUM_SEGMENTS; PART++)); do
    OFFSET=$((START_FRAME + PART * GOP_SIZE))
    OUTFILE="${INFILE}_r5_segment${PART}.bin"

    "$TMC2_BIN" \
      --configurationFolder="$CFG_BASE/" \
      --config="$CFG_COMMON" \
      --config="$CFG_CONDITION" \
      --config="$SEQ_CFG" \
      --config="$CFG_RATE" \
      --uncompressedDataPath="$PLY_INPUT" \
      --startFrameNumber="$OFFSET" \
      --frameCount=$GOP_SIZE \
      --reconstructedDataPath="$RECON_OUT" \
      --compressedStreamPath="$OUT_DIR/$OUTFILE"

    echo "Encoded $INFILE (part $PART, start frame: $OFFSET)  $OUTFILE"
  done
done
