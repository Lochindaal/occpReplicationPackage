# install local mona package and initialize folder structure

```bash
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
./run_experiments.sh 0
```
# Execute on-chain certification
```bash
./run_experiments.sh 1
```

# Post-processing
Calculates the average values from the obtained results:
* Average execution, recording, and replay time for the local experiments.
* Average certification time and executed expressions for the on-chain experiments.
```
python -u postprocessing.py
```

# Debug
```
# Note make sure the start location is set to the root of the project
runner/local_runner.py # executes the mona programs from the occp_config.ini locally
```
