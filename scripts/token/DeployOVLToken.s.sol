pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/OverlayV1Token.sol";

contract DeployOVLToken is Script {

  event logAddr(address addr);
  event logUint(uint256 num);

  function run() virtual external {

    address WALLET = vm.envAddress("WALLET");
    vm.startBroadcast(WALLET);

    deployOVLToken();

    vm.stopBroadcast();

  }

  function deployOVLToken () internal returns (address) {

    address FOUNDATION = vm.envAddress("FOUNDATION");
    OverlayV1Token token = new OverlayV1Token(FOUNDATION);

    return address(token);

  }

}
