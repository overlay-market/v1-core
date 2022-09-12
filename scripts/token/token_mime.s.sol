pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/mocks/TokenMock.sol";

contract DeployMimeToken is Script {

  function run () external {

    address deployer = 0x487AFA34296cD7d6cEEA2A6134AdEebd41d77E81;

    vm.startBroadcast(deployer);

    TokenMock mime = new TokenMock("Mime", "MIME", 8_000_000e18);

    vm.stopBroadcast();


  }

}
