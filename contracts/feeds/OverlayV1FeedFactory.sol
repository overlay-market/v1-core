// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";

abstract contract OverlayV1FeedFactory {
    uint256 immutable public microWindow;
    uint256 immutable public macroWindow;

    // registry of deployed feeds by factory
    mapping(address => bool) public isFeed;

    event FeedDeployed(address indexed user, address feed);

    constructor(uint256 _microWindow, uint256 _macroWindow) {
        microWindow = _microWindow;
        macroWindow = _macroWindow;
    }
}
