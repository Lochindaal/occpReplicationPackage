echo "Checking peer lists"
echo "Note: this only works if polygon is deployed locally without docker"
echo "          --> to check the peers connect to the container and run the commands inside"
polygon-edge --grpc-address 127.0.0.1:10000 peers list
polygon-edge --grpc-address 127.0.0.1:20000 peers list
polygon-edge --grpc-address 127.0.0.1:30000 peers list
polygon-edge --grpc-address 127.0.0.1:40000 peers list

echo "Checking balance"
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x9308aB927A9ce7E23CC6de5F2c7500b25185defF", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xB894BFFA4224dE2b2407Dc73Ff691A7aB8df0054", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x2725B14312053C7f20426801D8D473d9b80A20f9", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x699179f796061C375F4BfeFB746e1A3483d9F998", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x37Dd2e7300Ff4a161a34cf827f487bFc66104b27", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xf24091d69f296f8d5114f18e13395A3397b681E9", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x26E54FeF49dFFA71427D67c1125dE9EA087348a2", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x87dF767a82AD3d7e76e38307677596749dca9DB3", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x53BeefDA5f1f4Ba3650C92a8833380C1dfAE9cB8", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xc68c06558AbE131589b986916778A28F5029aC94", "latest"],"id":1}' localhost:10002
echo ""
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xB894BFFA4224dE2b2407Dc73Ff691A7aB8df0054", "latest"],"id":1}' localhost:10002
echo ""

echo "Get latest block"
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest", false],"id":1}' localhost:10002
echo ""
