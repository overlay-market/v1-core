// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

/// @notice A library for handling binary fixed point numbers
library FixedPoint160 {
    // TODO: test
    uint8 internal constant RESOLUTION = 160;
    uint256 internal constant Q160 = type(uint160).max + 1;
}
