# Overview

This repository contains code for the experiments of the SPIRIT Project "RABBTI@Scale: Exploring Real-Time Transcoding as a Service". 
Further, the repository also contains the showcase Demo at the EuroXR'25 conference.

# Table of Contents

- [Setup](#setup)
- [Stand-alone Transcoder](#Transcoder)
- [Experiments](#Experiments)
- [Demo](#Demo)
- [Further Information](#further-information)

# Setup
All you need is docker, and just to make your life easier.

```
snap install --edge --classic just
```
just can be installed through a number of ways, check out their github for alternatives.

# Transcoder
## Building the container
The just file wraps the transcoder container
```
just build-transcoder
```

### Running the container
``` 
just run-transcoder
```

### Utilities for inside the container
You can easily decode a bitstream with V-PCC using
```
just decode FILEPATH
```

# Experiments

### Test Data
Setting up requires you to pre-encode some data.
First, download some data using
```
  ./scripts/download_data.sh
```
Then, in the docker container:
```
  ./scripts/prepare_data.sh
```

# Demo
We include code for the demo at the EuroXR'25 conference in this repository. 
To showcase our system on consumer hardware, we use a downsampled variant of the point cloud content. 

## Running the Demo.
### 1 Device
If you want to run the Demo on one device, you can start it with
```
  docker compose -f docker-compose.demo.yaml up --build
```

### 2 Devices
If you want to run on 2 devices, make sure they are connected via ethernet and Port 8000 is opened on the server side device. Then, change the IP-Address in [docker-compose.demo-client.yaml](docker-compose.demo-client.yaml) to the IP of the server. 

On the server, start the transcoder with
```
  docker compose -f docker-compose.demo-server.yaml up --build
```
and on the client, run 
```
  docker compose -f docker-compose.demo-client.yaml up --build
```

### Visualizer and Control Pane
The Visualizer is now available on the Client device on http://localhost:5173 and the control pane is available through http://localhost:5000



# Further Information
TBA
