DOCKER_IMAGE := "pyrabbit"
DOCKER_TAG := "latest"


build:
	docker build -t {{DOCKER_IMAGE}}:{{DOCKER_TAG}} .

run:
	docker run --rm -it {{DOCKER_IMAGE}}:{{DOCKER_TAG}} 

clean: 
	docker image prune -f


# V-PCC Utilities
decode FILENAME:
	/app/dependencies/mpeg-pcc-tmc2/bin/PccAppDecoder \
		--compressedStreamPath={{FILENAME}} \
		--startFrameNumber=0 \
		--inverseColorSpaceConversionConfig=/app/dependencies/mpeg-pcc-tmc2/cfg/hdrconvert/yuv420torgb444.cfg \
		--reconstructedDataPath=/app/data/tmp/S26C03R03_dec_%04d.ply 