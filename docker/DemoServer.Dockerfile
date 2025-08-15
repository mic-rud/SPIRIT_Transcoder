FROM jrottenberg/ffmpeg:4.4-ubuntu2204

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    libegl1 \
    libgl1 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    curl \
    git \
    build-essential \
    cmake \
    vim \
    pkg-config \
    libclang-dev \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 \
    && ln -sf python3.10 /usr/bin/python3 \
    && ln -sf pip3 /usr/bin/pip \
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
WORKDIR /app/dependencies
RUN git clone https://github.com/benclmnt/tmc2-rs.git
RUN cd tmc2-rs && cargo build --release --bin decoder

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
#ENTRYPOINT ["/bin/bash"]

ENTRYPOINT []
CMD ["python3", "/app/src/run_demo_server.py"]