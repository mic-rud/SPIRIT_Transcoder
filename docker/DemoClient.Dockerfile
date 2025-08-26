FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1
ENV PKG_CONFIG_ALLOW_SYSTEM_LIBS=1

RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
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

# Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install "maturin[patchelf]"

# Fast tmc2 decoder
WORKDIR /app/dependencies/
COPY ./dependencies /app/dependencies
#RUN git clone https://github.com/mic-rud/tmc2-rs
WORKDIR /app/dependencies/tmc2-rs
RUN maturin build --release -o dist
RUN python3 -m pip install dist/*.whl

WORKDIR /app

CMD ["python3", "src/demo/client.py"]