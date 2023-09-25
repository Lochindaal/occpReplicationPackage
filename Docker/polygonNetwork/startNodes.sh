#!/bin/bash

# Start Polygon Node 1
polygon-edge server --data-dir ./test-chain-1 --chain genesis.json --grpc-address :10000 --libp2p :10001 --jsonrpc :10002 --seal --log-level debug &
# Start Polygon Node 2
polygon-edge server --data-dir ./test-chain-2 --chain genesis.json --grpc-address :20000 --libp2p :20001 --jsonrpc :20002 --seal --log-level debug &
# Start Polygon Node 3
polygon-edge server --data-dir ./test-chain-3 --chain genesis.json --grpc-address :30000 --libp2p :30001 --jsonrpc :30002 --seal --log-level debug &
# Start Polygon Node 4
polygon-edge server --data-dir ./test-chain-4 --chain genesis.json --grpc-address :40000 --libp2p :40001 --jsonrpc :40002 --seal --log-level debug  
