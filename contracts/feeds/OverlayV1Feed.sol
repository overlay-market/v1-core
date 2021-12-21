// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";

abstract contract OverlayV1Feed {
    using Oracle for Oracle.Data;

    uint256 immutable public microWindow;
    uint256 immutable public macroWindow;

    Oracle.Data public oracleDataLast;

    constructor(uint256 _microWindow, uint256 _macroWindow) {
        microWindow = _microWindow;
        macroWindow = _macroWindow;
    }

    /// @dev returns freshest possible data from oracle
    function latest() external returns (Oracle.Data memory) {
        Oracle.Data memory data = oracleDataLast;
        if (block.timestamp > data.timestamp) {
            data = _fetch();
            oracleDataLast = data;
        }
        return data;
    }

    /// @dev fetches data from oracle. should be implemented differently
    /// @dev for each feed type
    function _fetch() internal virtual returns (Oracle.Data memory);
}
