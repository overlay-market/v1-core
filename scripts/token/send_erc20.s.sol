pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../contracts/mocks/TokenMock.sol";

contract SendERC20 is Script {

  function run () external {


    address WALLET = vm.envAddress("WALLET");
    address TO = vm.envAddress("TO");

    vm.startBroadcast(WALLET);

    TokenMock mime = TokenMock(0x29FA8E130378bD2A7Aa4019a2ed873744a03778E);

    mime.transfer(TO, 4_000_000e18);

    vm.stopBroadcast();


  }

}
