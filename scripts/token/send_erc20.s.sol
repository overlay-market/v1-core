pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/mocks/TokenMock.sol";

contract SendERC20 is Script {

  function run () external {

    address deployer = 0x487AFA34296cD7d6cEEA2A6134AdEebd41d77E81;

    vm.startBroadcast(deployer);

    TokenMock mime = TokenMock(0x29FA8E130378bD2A7Aa4019a2ed873744a03778E);

    mime.transfer(0x8e8b3e19717A5DDCfccce9Bf3b225E61efDD7937, 4_000_000e18);

    vm.stopBroadcast();


  }

}
