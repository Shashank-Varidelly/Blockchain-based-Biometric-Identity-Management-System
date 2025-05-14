module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "5777",
      gas: 8000000,        // Keep this as is since we’re increasing Ganache’s limit
      gasPrice: 20000000000
    }
  },
  compilers: {
    solc: {
      version: "0.8.21",
      settings: {
        evmVersion: "istanbul"
      }
    }
  }
};