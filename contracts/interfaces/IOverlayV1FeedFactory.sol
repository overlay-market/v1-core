// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "../libraries/Oracle.sol";

interface IOverlayV1FeedFactory {
    function isFeed(address) external view returns (bool);
}
