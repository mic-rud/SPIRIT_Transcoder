## Setup

All you need is docker, and just to make your life easier.
```
snap install --edge --classic just
```
just can be installed through a number of ways, check out their github for alternatives.

### Building the container
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


## Test Data
Setting up requires you to pre-encode some data.
First, download some data using
```
  ./scripts/download_data.sh
```
Then, in the docker container:
```
  ./scripts/prepare_data.sh
```

## Demo
We include code for the demo at the XX conference here:

To showcase our system on lower end hardware, we use a downsampled variant of the point cloud.
It can be prepared from the 8iVFBv2 dataset (see above section for a download script) with the following code:



----
## Overview of scripts

In the scripts folder, we provide a number of scripts to ease development.

DESCRIBE

----
## Setup
Setup a virtual environment

We need pybindings
```
python -m pip install -r requirements.txt
sudo apt install build-essential cmake
```

Clone the VPCC tmc 2 codec:
```
cd dependencies
git clone https://github.com/MPEGGroup/mpeg-pcc-tmc2.git
```

Create python bindings:
```
mkdir build && cd build
cmake .. \
  -DPYTHON_EXECUTABLE=$(pyenv which python) \
  -DCMAKE_PREFIX_PATH=$(python -m pybind11 --cmakedir) 
make 
```

## Path V-PCC
In order to generate bindings for the Bitstream Parsing, we need to patch V-PCC
```
./patch.sh
```

## Sym-Link
Add a symbolic link if the module is not found on import
```
ln -s /PATH/TO/build/bindings/bitstream_bindings.cpython-<pyversion>-x86_64-linux-gnu.so .venv/lib/python<pyversion>/site-packages/bitstream_bindings.so
```