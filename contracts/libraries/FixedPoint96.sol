// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

/// @notice A library for handling binary fixed point numbers
library FixedPoint96 {
    // TODO: test
    uint8 internal constant RESOLUTION = 96;
    uint256 internal constant Q96 = type(uint96).max + 1;
}
