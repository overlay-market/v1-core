pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/OverlayV1Token.sol";

contract DeployOVLToken is Script {

  event logAddr(address addr);
  event logUint(uint256 num);

  function run() external {

    address WALLET = vm.envAddress("WALLET");
    vm.startBroadcast(WALLET);

    deployOVL();

    vm.stopBroadcast();

  }

  function deployOVL () internal {

    address FOUNDATION = vm.envAddress("FOUNDATION");
    OverlayV1Token token = new OverlayV1Token(FOUNDATION);

  }

}
