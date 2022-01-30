// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "./FixedPoint.sol";

library Oracle {
    using FixedPoint for uint256;
    struct Data {
        uint256 timestamp;
        uint256 microWindow;
        uint256 macroWindow;
        uint256 priceOverMicroWindow; // p(now) averaged over micro
        uint256 priceOverMacroWindow; // p(now) averaged over macro
        uint256 priceOverMicroWindowOneWindowAgo; // p(now - micro) averaged over micro
        uint256 priceOverMacroWindowOneWindowAgo; // p(now - macro) averaged over macro
        uint256 reserveOverMicroWindow; // r(now) in ovl averaged over micro
        uint256 reserveOverMacroWindow; // r(now) in ovl averaged over macro
        bool hasReserve; // whether oracle has manipulable reserve pool
    }

    // TODO: reduce to what we need for gas purposes
    // NEED: priceOverMicroWindow, priceOverMacroWindow, reserveOverMicroWindow, priceOverMacroWindowOneWindowAgo
}
