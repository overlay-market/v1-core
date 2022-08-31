// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.4;

import "forge-std/Script.sol";
import "../src/Portal.sol";

contract PortalScript is Script {
    address EndPoint = 0x79a63d6d8BBD5c6dfc774dA79bCcD948EAcb53FA; // for other address https://layerzero.gitbook.io/docs/technical-reference/testnet/testnet-addresses

    function setUp() public {}

    function run() public {
        vm.broadcast();

        Portal portal = new Portal(EndPoint);

        vm.stopBroadcast();
    }
}

// forge create --rpc-url https://rinkeby.arbitrum.io/rpc --constructor-args 0x4D747149A57923Beb89f22E6B7B97f7D8c087A00 --private-key 0xdede1c90cd9ca110ccc0fbcff58ccbb65cbb37a95f63acd543e5c7963a7f6fba contracts/Foundry/Portal.sol:Portal --etherscan-api-key 7YNIM4192HFF7NXSK1SWWBIN3ZI2EYAQCK --verify
// forge create --rpc-url https://rinkeby.infura.io/v3/429eb57532b54560b1d4cc4201724bf0 --constructor-args 0x79a63d6d8BBD5c6dfc774dA79bCcD948EAcb53FA --private-key 0xdede1c90cd9ca110ccc0fbcff58ccbb65cbb37a95f63acd543e5c7963a7f6fba contracts/Foundry/Portal.sol:Portal --etherscan-api-key U772ATWP1Z8J3MNMFUXXFPYD213PEVEXAZ --verify