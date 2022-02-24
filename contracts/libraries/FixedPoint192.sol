// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

/// @notice A library for handling binary fixed point numbers
library FixedPoint192 {
    // TODO: test
    uint8 internal constant RESOLUTION = 192;
    uint256 internal constant Q192 = type(uint192).max + 1;
}
