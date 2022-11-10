// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "forge-std/Script.sol";

interface Name { function name () external returns (string memory); }

contract Simulation is Script {

  function run () public {

    string memory name = Name(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48).name();

    console.log(name);

  }

}
