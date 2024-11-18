#!/bin/bash

# Build solidity contract
npx hardhat compile

# Deploy contracts to the polygon network
while true; do
	line_count=$(wc -l < contracts.dat)
    
	if [[ $line_count -ge 30 ]]; then
		break
	fi
	echo $line_count
	HARDHAT_IGNORE_NODE_VERSION=true npx --no-warnings hardhat run scripts/deploy.js --network polygon_loc | grep "Contract deployed" | awk '{print $4}' >> contracts.dat
	sleep 4
done

cp contracts.dat ../../../data/ecs/contract_list.dat
