// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "./FixedPoint.sol";

library Oracle {
    using FixedPoint for uint256;
    struct Data {
        uint256 timestamp;
        uint256 microWindow;
        uint256 macroWindow;
        uint256 priceOverMicroWindow;
        uint256 priceOverMacroWindow;
        uint256 reservesOverMicroWindow; // in ovl
        uint256 reservesOverMacroWindow; // in ovl
    }
}
