pragma solidity ^0.8.10;

import "forge-std/Script.sol";

import "../../contracts/OverlayV1Factory.sol";


contract DeployMarketFactory is Script {

  function run () virtual external {

    address deployer = vm.envAddress("WALLET");
    vm.startBroadcast(deployer);

    deployMarketFactory(address(0));

    vm.stopBroadcast();

  }
  
  function deployMarketFactory (address _ovl) internal returns (address) {

    address OVL_TOKEN = _ovl == address(0) 
      ? vm.envAddress("OVL_TOKEN") 
      : _ovl;
    address FOUNDATION = vm.envAddress("FOUNDATION");

    OverlayV1Factory factory = new OverlayV1Factory(OVL_TOKEN, FOUNDATION);

    return address(factory);

  }

}
