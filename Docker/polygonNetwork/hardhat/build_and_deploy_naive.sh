#!/bin/bash

# Build solidity contract
npx hardhat compile

# Deploy contracts to the polygon network
while true; do
	line_count=$(wc -l < contracts_naive.dat)
    
	if [[ $line_count -ge 30 ]]; then
		break
	fi
	echo $line_count
	HARDHAT_IGNORE_NODE_VERSION=true npx --no-warnings hardhat run scripts/deployNaive.js --network polygon_loc | grep "Contract deployed" | awk '{print $4}' >> contracts_naive.dat
	sleep 5
done

cp contracts_naive.dat ../../../data/ecs/contract_list_naive.dat
