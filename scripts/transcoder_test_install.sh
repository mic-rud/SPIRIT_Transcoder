#!/bin/bash

sudo apt update
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  software-properties-common \
  git

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce -y

sudo systemctl start docker
sudo systemctl enable docker

#Git repo 
git clone https://github.com/mic-rud/SPIRIT_Transcoder.git
cd SPIRIT_Transcoder

#Docker building
sudo docker build -t transcoder -f ./docker/Transcoder.Dockerfile .

#Docker running
sudo docker run --rm -it \
  -v ./data:/app/data:z \
  -v ./configs:/app/configs:z \
  -v ./results:/app/results:z \
  transcoder