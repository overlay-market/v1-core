// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../libraries/Risk.sol";

contract RiskMock {
    using Risk for uint256[15];

    // risk params
    uint256[15] public params; // params.idx order based on Risk.Parameters enum

    function get(Risk.Parameters name) external view returns (uint256) {
        return params.get(name);
    }

    function set(Risk.Parameters name, uint256 value) external {
        params.set(name, value);
    }

    function getEnumFromUint(uint256 idx) external view returns (Risk.Parameters name) {
        return Risk.Parameters(idx);
    }
}
