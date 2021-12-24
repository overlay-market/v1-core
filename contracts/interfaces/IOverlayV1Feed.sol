// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";

interface IOverlayV1Feed {
    function latest() external view returns (Oracle.Data memory);
}
