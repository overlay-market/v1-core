// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";

abstract contract OverlayV1Feed {
    using Oracle for Oracle.Data;

    uint256 immutable public microWindow;
    uint256 immutable public macroWindow;

    constructor(uint256 _microWindow, uint256 _macroWindow) {
        microWindow = _microWindow;
        macroWindow = _macroWindow;
    }

    /// @dev returns freshest possible data from oracle
    function latest() external view returns (Oracle.Data memory) {
        return _fetch();
    }

    /// @dev fetches data from oracle. should be implemented differently
    /// @dev for each feed type
    function _fetch() internal view virtual returns (Oracle.Data memory);
}
