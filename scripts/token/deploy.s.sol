pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/OverlayV1Token.sol";

contract DeployToken is Script {

  function run() external {

    vm.startBroadcast(0x3857d718f8a1E9E8DBd3072BE9bc5105c5d21158);

    OverlayV1Token token = new OverlayV1Token();

    vm.stopBroadcast();

  }

}
