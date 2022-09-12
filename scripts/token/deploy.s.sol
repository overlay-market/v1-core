pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/OverlayV1Token.sol";

contract DeployToken is Script {

  function run() external {

    vm.startBroadcast(0x487AFA34296cD7d6cEEA2A6134AdEebd41d77E81);

    OverlayV1Token token = new OverlayV1Token();

    vm.stopBroadcast();

  }

}
