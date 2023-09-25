#!/bin/bash

#docker buildx build --network=host --build-context project=. .
# Build the Docker image using the Dockerfile
#docker build --network=host -t polygon-image:latest .
docker build -t polygon-image:latest .

#docker rm polygon-container
## Create a Docker container from the image
##docker run -d --name polygon-container \
#docker run --name polygon-container \
#  -v $(pwd)/test-chain-1:/test-chain-1 \
#  -v $(pwd)/test-chain-2:/test-chain-2 \
#  -v $(pwd)/test-chain-3:/test-chain-3 \
#  -v $(pwd)/test-chain-4:/test-chain-4 \
#  polygon-image
  #-v $(pwd)/genesis.json:/genesis.json \

# You can add more commands here if needed
