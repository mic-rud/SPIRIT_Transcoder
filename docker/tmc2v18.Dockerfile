FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1
ENV PKG_CONFIG_ALLOW_SYSTEM_LIBS=1

RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3.10-distutils \
    libegl1 libgl1-mesa-glx libgl1-mesa-dri \
    libxml2-dev libpng-dev \
    libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
    curl git build-essential cmake pkg-config libclang-dev vim \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 \
    && ln -sf /usr/bin/python3.10 /usr/bin/python3 \
    && ln -sf /usr/bin/pip3 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*


# Cargo and just
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN cargo install just

RUN curl -LO https://github.com/Kitware/CMake/releases/download/v3.27.9/cmake-3.27.9-linux-x86_64.sh && \
    chmod +x cmake-3.27.9-linux-x86_64.sh && \
    ./cmake-3.27.9-linux-x86_64.sh --skip-license --prefix=/usr/local && \
    rm cmake-3.27.9-linux-x86_64.sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install pybind11

# Clone and build VPCC codec (v18 for demo)
WORKDIR /app/dependencies
RUN git clone --branch release-v18.0 --depth=1 https://github.com/MPEGGroup/mpeg-pcc-tmc2.git

# Build and Patch VPCC
WORKDIR /app/dependencies/mpeg-pcc-tmc2
COPY patch.sh /app/dependencies/mpeg-pcc-tmc2/patch.sh

RUN ls -l /app/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h && \
    cat /app/dependencies/mpeg-pcc-tmc2/patch.sh && \
    chmod +x /app/dependencies/mpeg-pcc-tmc2/patch.sh && \
    /app/dependencies/mpeg-pcc-tmc2/patch.sh && \
    grep "SampleStreamV3CUnit" /app/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h || (echo "Patch failed"; exit 1)

RUN mkdir build && cd build \
    && cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    && make -j$(nproc)

# Build tmc2 real time decoder 
RUN pip install "maturin[patchelf]"

# Fast tmc2 decoder
WORKDIR /app/dependencies/
RUN git clone https://github.com/mic-rud/tmc2-rs
WORKDIR /app/dependencies/tmc2-rs
RUN maturin build --release -o dist
RUN python3 -m pip install dist/*.whl


# Build Transcoder
WORKDIR /app
COPY . /app
RUN mkdir build && cd build \
   && cmake .. \
       -DPYTHON_EXECUTABLE=$(which python3) \
       -DCMAKE_PREFIX_PATH=$(python3 -m pybind11 --cmakedir) \
   && make

# Add symlink
RUN ln -s /app/build/bindings/bitstream_bindings.cpython-310-x86_64-linux-gnu.so \
   /usr/local/lib/python3.10/dist-packages/bitstream_bindings.so

WORKDIR /app

# Force entrypoint
ENTRYPOINT ["/bin/bash"]
