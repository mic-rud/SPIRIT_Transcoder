sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y git
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y
sudo apt update
sudo apt install docker-ce -y
sudo systemctl start docker
sudo systemctl enable docker

git clone git@github.com:mic-rud/SPIRIT_Transcoder.git
cd SPIRIT_Transcoder

docker build -t transcoder -f ./docker/Transcoder.Dockerfile .
docker run --rm -it -v ./data:/sapapp/data:z -v ./src:/app/src:z -v ./configs:/app/configs:z -v ./docker:/app/docker:z transcoder
docker run --rm -it \
  -v ./data:/app/data:z \
  -v ./configs:/app/configs:z \
  -v ./results:/app/results:z \
  transcoder