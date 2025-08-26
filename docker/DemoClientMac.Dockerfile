FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive \
    PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 \
    PKG_CONFIG_ALLOW_SYSTEM_LIBS=1

# 1) First update over the default *http* mirrors and install CA certs
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates wget gnupg \
 && rm -rf /var/lib/apt/lists/*

# 2) (Optional but nice) switch to https now that CAs exist
RUN sed -i 's|http://|https://|g' /etc/apt/sources.list

# 3) Now your real install
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential cmake pkg-config libclang-dev vim \
    python3 python3-dev python3-distutils python3-pip \
    ffmpeg \
    libegl1 libgl1-mesa-glx libgl1-mesa-dri \
    libxml2-dev libpng-dev \
    libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
 && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python && ln -sf /usr/bin/pip3 /usr/bin/pip

# Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN cargo install just

# Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install maturin[patchelf]  

# Fast tmc2 decoder
WORKDIR /app/dependencies/
COPY ./dependencies /app/dependencies
WORKDIR /app/dependencies/tmc2-rs
RUN maturin build --release -o dist && python -m pip install dist/*.whl

WORKDIR /app
CMD ["python", "src/demo/client.py"]
