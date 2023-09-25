#!/bin/bash

#docker buildx build --network=host --build-context project=. .
# Build the Docker image using the Dockerfile
#docker build --network=host -t polygon-image .

docker rm polygon-container
## Create a Docker container from the image
##docker run -d --name polygon-container \
docker run --name polygon-container -d \
	-v $(pwd)/test-chain-1:/test-chain-1 \
	-v $(pwd)/test-chain-2:/test-chain-2 \
	-v $(pwd)/test-chain-3:/test-chain-3 \
	-v $(pwd)/test-chain-4:/test-chain-4 \
	-p 10000:10000 -p 10001:10001 -p 10002:10002 \
	-p 20000:20000 -p 20001:20001 -p 20002:20002 \
	-p 30000:30000 -p 30001:30001 -p 30002:30002 \
	-p 40000:40000 -p 40001:40001 -p 40002:40002 \
  	polygon-image:latest
  #-v $(pwd)/genesis.json:/genesis.json \

# You can add more commands here if needed
