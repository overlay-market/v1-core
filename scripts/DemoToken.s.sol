// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.4;

import "forge-std/Script.sol";
import "../src/DemoToken.sol";

contract DemoTokenScript is Script {

    function setUp() public {}

    function run() public {
        vm.broadcast();

        DemoToken demoToken = new DemoToken('Demo Token', 'DT', 1000000000000000000000);

        vm.stopBroadcast();
    }
}

// forge create --rpc-url https://rinkeby.infura.io/v3/429eb57532b54560b1d4cc4201724bf0 --constructor-args 'Demo Token', 'DT', 1000000000000000000000 --private-key 0xdede1c90cd9ca110ccc0fbcff58ccbb65cbb37a95f63acd543e5c7963a7f6fba contracts/Foundry/DemoToken.sol:DemoToken --etherscan-api-key U772ATWP1Z8J3MNMFUXXFPYD213PEVEXAZ --verify
// forge create --rpc-url https://rinkeby.arbitrum.io/rpc --constructor-args 'Demo Token', 'DT', 1000000000000000000000 --private-key 0xdede1c90cd9ca110ccc0fbcff58ccbb65cbb37a95f63acd543e5c7963a7f6fba contracts/Foundry/DemoToken.sol:DemoToken --etherscan-api-key 7YNIM4192HFF7NXSK1SWWBIN3ZI2EYAQCK --verify
