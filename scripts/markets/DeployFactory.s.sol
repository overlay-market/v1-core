pragma solidity ^0.8.10;

import "forge-std/Script.sol";

import "../../contracts/OverlayV1Factory.sol";


contract DeployFactory is Script {

  function run () external {

    address deployer = vm.envAddress("WALLET");
    vm.startBroadcast(deployer);

    deployFactory();

    vm.stopBroadcast();

  }
  
  function deployFactory () internal {

    address OVL_TOKEN = vm.envAddress("OVL_TOKEN");
    address FOUNDATION = vm.envAddress("FOUNDATION");

    OverlayV1Factory factory = new OverlayV1Factory(OVL_TOKEN, FOUNDATION);

  }

}
