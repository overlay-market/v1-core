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
        // sanity checks on micro and macroWindow
        require(_microWindow > 0, "OVLV1Feed: microWindow == 0");
        require(_macroWindow >= _microWindow, "OVLV1Feed: macroWindow < microWindow");
        require(_macroWindow <= 86400, "OVLV1Feed: macroWindow > 1 day");

        // set the immutables
        microWindow = _microWindow;
        macroWindow = _macroWindow;
        feedFactory = msg.sender;
    }

    /// @dev returns freshest possible data from oracle
    function latest() external view returns (Oracle.Data memory) {
        return _fetch();
    }

    /// @dev fetches data from oracle. should be implemented differently
    /// @dev for each feed type
    function _fetch() internal view virtual returns (Oracle.Data memory);
}
