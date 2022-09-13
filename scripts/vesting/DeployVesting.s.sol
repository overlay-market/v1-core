pragma solidity 0.8.10;

import "forge-std/Script.sol";
import "@overlay/council/contracts/vaults/VestingVault.sol";

contract DeployVesting is Script {

  function run () external {

    address WALLET = vm.envAddress("WALLET");
    vm.startBroadcast(WALLET);


    vm.stopBroadcast();

  }

  function deployVestingVault () internal {

    address OVL = vm.envAddress("OVL_TOKEN");

  }

}
