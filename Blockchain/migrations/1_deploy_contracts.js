const FaceRegistry = artifacts.require("FaceRegistry");
module.exports = function (deployer) {
  deployer.deploy(FaceRegistry);
};