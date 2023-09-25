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
# ToDo add script!
```
# Execute on-chain certification
```bash
# ToDo add script!
```

# Debug

```
# Note make sure the start location is set to the root of the project
runner/local_runner.py # executes the mona programs from the occp_config.ini locally
```
