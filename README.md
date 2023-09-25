# install local mona package and initialize folder structure

```bash
pip install -r requirements.txt
pip install -r mona/requirements.txt
chmod +x setup.sh
./setup.sh
```

# Run environment dependencies
```bash
# Polygon network
cd Docker/polygonNetwork
./build_poly.sh
./run_polygon.sh

# contract deployment
cd hardhat
npm install
./build_and_deploy.sh

# S3 storage
cd Docker/localstack
docker-compose up
```

Note: re-deploying polygon requires the deletion of all volumes, due to the creation of new security keys!

# Execute local MONA run
```bash
mkdir -p data/logs
./run_experiments.sh 0
```
# Execute on-chain certification
```bash
mkdir -p data/logs
./run_experiments.sh 1
```

# Post-processing
Calculates the average values from the obtained results:
* Average execution, recording, and replay time for the local experiments.
* Average certification time and executed expressions for the on-chain experiments.
```
python -u postprocessing.py
```

# Structure
```bash
data/
|-- archives
|   |-- contains compressed execution logs from local Mona run 
|-- ecs --> contains blockchain related data
|   |-- contract_addresses.json
|   |-- contract_list.dat
|   |-- ecs_smart_contract.sol --> solidity contract
|   |-- smart_contract_abi.json
|   `-- wallets.json
|-- programs
|   `-- contains example programs written in Mona
`-- results
    |-- local
    |   |-- avg_results.json --> produced after post-processing
    |   |-- local_results.json --> results from local MONA run
    |   `-- local_results.pickle --> results from local MONA run
    |-- occp
    |   |-- avg_results.json --> produced after post-processing
    |   |-- avg_worker_results.json --> results from each worker
    |   `-- results.json --> results from on-chain run
```

# Debug
```
# Note make sure the start location is set to the root of the project
runner/local_runner.py # executes the mona programs from the occp_config.ini locally
```
