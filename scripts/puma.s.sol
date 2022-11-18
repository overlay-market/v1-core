// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "forge-std/Script.sol";

import "../contracts/OverlayV1PUMA.sol";

interface Name { function name () external returns (string memory); }

contract Simulation is Script {

  function run () public {

    string memory name = Name(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48).name();

    // use uni for now
    address weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address ovl = 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984;
    address spot = 0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801;

    OverlayV1PUMA PUMA = new OverlayV1PUMA(ovl, spot);

    // PUMA.detect(600);

    PUMA.nextTick();

  }

}