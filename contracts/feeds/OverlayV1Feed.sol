// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "../interfaces/feeds/IOverlayV1Feed.sol";
import "../libraries/Oracle.sol";

abstract contract OverlayV1Feed is IOverlayV1Feed {
    using Oracle for Oracle.Data;

    address public immutable feedFactory;
    uint256 public immutable microWindow;
    uint256 public immutable macroWindow;

    constructor(uint256 _microWindow, uint256 _macroWindow) {
        // set the immutables
        microWindow = _microWindow;
        macroWindow = _macroWindow;
        feedFactory = msg.sender;
    }

    /// @dev Returns freshest possible data from oracle
    /// @return Past snapshot values to calculate the TWAP
    function latest() external view returns (Oracle.Data memory) {
        return _fetch();
    }

    /// @dev Fetches data from oracle.
    /// @dev Should be implemented differently for every Oracle's feed type
    /// @dev For each feed type
    /// @return Past snapshot values to calculate the TWAP
    function _fetch() internal view virtual returns (Oracle.Data memory);
}
