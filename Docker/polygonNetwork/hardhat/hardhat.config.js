require('dotenv').config({ path: './.env.docker' });
require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-etherscan");

module.exports = {
  defaultNetwork: "polygon_loc",
  networks: {
    hardhat: {
    },
    polygon_loc: {
		url: "http://localhost:10002",
		accounts: [process.env.PRIVATE_KEY]
	},
  },
  solidity: {
    version: "0.8.9",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
}
