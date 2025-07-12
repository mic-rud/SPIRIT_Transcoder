TRANSCODER_IMAGE := "pyrabbit-transcoder"
DEMO_IMAGE := "pyrabbit-demo"
DOCKER_TAG := "latest"


build-transcoder:
	docker build -t {{TRANSCODER_IMAGE}}:{{DOCKER_TAG}} -f ./docker/Transcoder.Dockerfile .

run-transcoder:
	docker run --rm -it -v ./data:/app/data:z -v ./src:/app/src:z -v ./configs:/app/configs:z -v ./docker:/app/docker:z {{TRANSCODER_IMAGE}}:{{DOCKER_TAG}} 

build-demo:
	docker build -t {{DEMO_IMAGE}}:{{DOCKER_TAG}} -f ./docker/Demo.Dockerfile .

run-demo:
	docker run --rm -it -v /tmp:/tmp -v ./data:/app/data {{DEMO_IMAGE}}:{{DOCKER_TAG}} 

clean: 
	docker image prune -f


# V-PCC Utilities
decode FILENAME:
	/app/dependencies/mpeg-pcc-tmc2/bin/PccAppDecoder \
		--compressedStreamPath=/app/data/transcoded/{{FILENAME}} \
		--startFrameNumber=0 \
		--inverseColorSpaceConversionConfig=/app/dependencies/mpeg-pcc-tmc2/cfg/hdrconvert/yuv420torgb444.cfg \
		--reconstructedDataPath=/app/data/reconstructed/S26C03R03_dec_%04d.ply 

transcode:
	python3.10 /app/src/main.py

encode INFILE OUTFILE:
	/app/dependencies/mpeg-pcc-tmc2/bin/PccAppEncoder \
		--configurationFolder=/app/dependencies/mpeg-pcc-tmc2/cfg/ \
		--config=/app/dependencies/mpeg-pcc-tmc2/cfg/common/ctc-common.cfg \
		--config=/app/dependencies/mpeg-pcc-tmc2/cfg/condition/ctc-all-intra.cfg \
		--config=/app/dependencies/mpeg-pcc-tmc2/cfg/sequence/{{INFILE}}_vox10.cfg \
		--config=/app/dependencies/mpeg-pcc-tmc2/cfg/rate/ctc-r5.cfg \
		--profileReconstructionIdc=0 \
		--uncompressedDataPath=/app/data/{{INFILE}}/Ply/{{INFILE}}_vox10_%04d.ply \
		--frameCount=30 \
		--reconstructedDataPath=S26C03R03_rec_%04d.ply \
		--compressedStreamPath=/app/data/encoded/{{OUTFILE}}

rustdecode INFILE OUTPATH:
	cargo run --manifest-path /app/dependencies/tmc2-rs/Cargo.toml --bin decoder -- -i {{INFILE}} -o {{OUTPATH}}


metrics SOURCE RECONSTRUCTION:

# Render utilities
render INFILE OUTFILE:
	python3 ./tools/render.py {{INFILE}} data/tmp/{{OUTFILE}}
