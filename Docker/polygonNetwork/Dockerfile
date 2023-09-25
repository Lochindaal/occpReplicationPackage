# Use a base image with the necessary dependencies
FROM ubuntu:22.04

WORKDIR /poly
#COPY genesis.json /genesis.json
# Install required tools
RUN apt-get update && apt-get install -y curl tar

# Step 1: Download polygon-edge and set it up
RUN curl -L https://github.com/0xPolygon/polygon-edge/releases/download/v0.7.3-beta1/polygon-edge_0.7.3-beta1_linux_amd64.tar.gz --output polygon-edge.tar.gz && \
    tar -xvf polygon-edge.tar.gz && \
    mv polygon-edge /usr/local/bin && \
    polygon-edge version

# Step 2: Create secrets
RUN polygon-edge secrets init --insecure --data-dir test-chain-1 && \
    polygon-edge secrets init --insecure --data-dir test-chain-2 && \
    polygon-edge secrets init --insecure --data-dir test-chain-3 && \
    polygon-edge secrets init --insecure --data-dir test-chain-4

# Step 3: Get node ids for boot nodes
RUN NODE1=$(polygon-edge secrets output --data-dir test-chain-1) && \
    NODE1=$(echo $NODE1 | awk '{print $16}') && \
    NODE2=$(polygon-edge secrets output --data-dir test-chain-2) && \
    NODE2=$(echo $NODE2 | awk '{print $16}') && \
	echo $NODE1 && echo $NODE2 && \
	polygon-edge genesis --consensus ibft --ibft-validators-prefix-path test-chain- \
	--block-gas-limit 999000000000 \
	--bootnode /ip4/127.0.0.1/tcp/10001/p2p/$NODE1 \
	--bootnode /ip4/127.0.0.1/tcp/20001/p2p/$NODE2 \
   --premine=0x9308aB927A9ce7E23CC6de5F2c7500b25185defF:1000000000000000000000 \
   --premine=0x2725B14312053C7f20426801D8D473d9b80A20f9:1000000000000000000000 \
   --premine=0xB894BFFA4224dE2b2407Dc73Ff691A7aB8df0054:1000000000000000000000 \
   --premine=0x699179f796061C375F4BfeFB746e1A3483d9F998:1000000000000000000000 \
   --premine=0x37Dd2e7300Ff4a161a34cf827f487bFc66104b27:1000000000000000000000 \
   --premine=0xf24091d69f296f8d5114f18e13395A3397b681E9:1000000000000000000000 \
   --premine=0x26E54FeF49dFFA71427D67c1125dE9EA087348a2:1000000000000000000000 \
   --premine=0x87dF767a82AD3d7e76e38307677596749dca9DB3:1000000000000000000000 \
   --premine=0x53BeefDA5f1f4Ba3650C92a8833380C1dfAE9cB8:1000000000000000000000 \
   --premine=0xc68c06558AbE131589b986916778A28F5029aC94:1000000000000000000000 \
   --premine=0xC397F5EF32837a665D6DD81cf942fDc434c12497:1000000000000000000000 \
   --premine=0xBD3282F0c1Fd8e413db01131aCf31F2a6e4292A9:1000000000000000000000 \
   --premine=0x3C6EF4346B25f0Bf19D62cd2354473FD749060cA:1000000000000000000000 \
   --premine=0x84C0a90037c665bc938b619A062262DE614654e3:1000000000000000000000 \
   --premine=0x242FAB6e534152836908997857508EabA596b2Ed:1000000000000000000000 \
   --premine=0x7242bDD2cBb34098b884b5b0892d279B9FdB871a:1000000000000000000000 \
   --premine=0xe6E98b735390df3eF219b6E2Ce265D06EB19AF63:1000000000000000000000 \
   --premine=0x28BE96512e0BC22D09a96317522B4AE984D9b7D7:1000000000000000000000 \
   --premine=0x9aD33855F052b6F5b6e0aB8416AA0da990536b43:1000000000000000000000 \
   --premine=0x8e71931d58514bD14a205336Abdd091db075130c:1000000000000000000000

RUN apt-get install -y supervisor

# Copy the startNodes.sh script to the container
COPY startNodes.sh startNodes.sh
#COPY ./polygonNetwork/startNodes.sh /startNodes.sh

# Remove tar file to reduce size
RUN rm polygon-edge.tar.gz

# Version 1: working
## Make the script executable
RUN chmod +x startNodes.sh

## Define the entry point for the container to run the script
CMD ["/poly/startNodes.sh"]

# Version 2: Something wrong with connection!
## Create a supervisord configuration file
#RUN echo "[program:polygon]" >> /etc/supervisor/conf.d/polygon.conf
#RUN echo "command=/poly/startNodes.sh" >> /etc/supervisor/conf.d/polygon.conf
#RUN echo "autostart=true" >> /etc/supervisor/conf.d/polygon.conf
### Use supervisord as the main entry point
#CMD ["supervisord", "-n"]
