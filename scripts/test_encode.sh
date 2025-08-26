/app/dependencies/mpeg-pcc-tmc2/bin/PccAppEncoder \
  --configurationFolder="/app/dependencies/mpeg-pcc-tmc2/cfg/" \
  --config="/app/dependencies/mpeg-pcc-tmc2/cfg/common/ctc-common.cfg" \
  --config="/app/dependencies/mpeg-pcc-tmc2/cfg/condition/ctc-all-intra.cfg" \
  --config="/app/dependencies/mpeg-pcc-tmc2/cfg/rate/ctc-r5.cfg" \
  --config="/app/configs/tmc2_configs/longdress_vox9.cfg" \
  --uncompressedDataPath="/app/data/downsampled/loot/longdress_vox10_%04d.ply" \
  --startFrameNumber=1000 \
  --keepIntermediateFiles=1 \
  --frameCount=3 \
  --resolution=511 \
  --occupancyPrecision=1 \
  --profileReconstructionIdc=0 \
  --compressedStreamPath="/app/data/encoded/longdress_test_vox9.bin" 
  #--config="/app/dependencies/mpeg-pcc-tmc2/cfg/sequence/loot_vox10.cfg" \
