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