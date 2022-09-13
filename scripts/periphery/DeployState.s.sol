pragma solidity ^0.8.10;

import "@overlay/v1-periphery/contracts/OverlayV1State.sol";
import "@overlay/v1-core/contracts/interfaces/IOverlayV1Factory.sol";
import "forge-std/Script.sol";

contract DeployState is Script {


  function run () external {

    address WALLET = vm.envAddress("WALLET");

    vm.startBroadcast(WALLET);

    deployState();

    vm.stopBroadcast();

  }

  function deployState () internal {

    address FACTORY = vm.envAddress("OVL_V1_FACTORY");

    OverlayV1State state = new OverlayV1State(IOverlayV1Factory(FACTORY));

  }

}
