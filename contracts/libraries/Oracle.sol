// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

library Oracle {
    /// @notice Past snapshot values to calculate the TWAP.
    /// @dev Every Oracle's data must be formatted to conform to this struct.
    struct Data {
        uint256 timestamp;
        uint256 microWindow;
        uint256 macroWindow;
        uint256 priceOverMicroWindow; // p(now) averaged over micro
        uint256 priceOverMacroWindow; // p(now) averaged over macro
        uint256 priceOneMacroWindowAgo; // p(now - macro) avg over macro
        uint256 reserveOverMicroWindow; // r(now) in ovl averaged over micro
        bool hasReserve; // whether oracle has manipulable reserve pool
    }
}
