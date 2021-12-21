// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";

interface IOverlayFeed {
    function latest() external returns (Oracle.Data memory);
}
