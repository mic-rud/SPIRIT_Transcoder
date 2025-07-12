FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3.10 \
    python3.10-dev \
    python3-pip \
    vim \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cargo and just
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN cargo install just

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install pybind11

# Clone and build VPCC codec
WORKDIR /app/dependencies
RUN git clone https://github.com/MPEGGroup/mpeg-pcc-tmc2.git

# Build and Patch VPCC
WORKDIR /app/dependencies/mpeg-pcc-tmc2
COPY patch.sh /app/dependencies/mpeg-pcc-tmc2/patch.sh

RUN ls -l /app/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h && \
    cat /app/dependencies/mpeg-pcc-tmc2/patch.sh && \
    chmod +x /app/dependencies/mpeg-pcc-tmc2/patch.sh && \
    /app/dependencies/mpeg-pcc-tmc2/patch.sh && \
    grep "SampleStreamV3CUnit" /app/dependencies/mpeg-pcc-tmc2/source/lib/PccLibBitstreamWriter/include/PCCBitstreamWriter.h || (echo "Patch failed"; exit 1)

RUN rm -rf build && mkdir build && cd build \
    && cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    && make -j$(nproc)


# Build Transcoder
WORKDIR /app
COPY . /app

RUN rm -rf build && mkdir build && cd build \
   && cmake .. \
       -DPYTHON_EXECUTABLE=$(which python3) \
       -DCMAKE_PREFIX_PATH=$(python3 -m pybind11 --cmakedir) \
   && make

# Add symlink
RUN ln -s /app/build/bindings/bitstream_bindings.cpython-310-x86_64-linux-gnu.so \
   /usr/local/lib/python3.10/dist-packages/bitstream_bindings.so

ENV XDG_RUNTIME_DIR=/tmp/runtime-root
RUN mkdir -p /tmp/runtime-root

WORKDIR /app/src
CMD ["/bin/bash"]