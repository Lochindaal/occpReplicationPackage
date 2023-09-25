#!/bin/bash

# Build solidity contract
npx hardhat compile

# Deploy contracts to the polygon network
for i in {1..30}
do
	echo $i
	HARDHAT_IGNORE_NODE_VERSION=true npx --no-warnings hardhat run scripts/deploy.js --network polygon_loc | grep "Contract deployed" | awk '{print $4}' >> contracts.dat
	sleep 3
done

cp contracts.dat ../../../data/ecs/contract_list.dat
