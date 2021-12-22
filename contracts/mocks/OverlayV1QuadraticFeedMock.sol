// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";
import "../feeds/OverlayV1Feed.sol";

contract OverlayV1QuadraticFeedMock is OverlayV1Feed {

    uint256 immutable public deployed;

    uint256 immutable public mPrice;
    uint256 immutable public mReserve;

    constructor(
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _mPrice,
        uint256 _mReserve
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        mPrice = _mPrice;
        mReserve = _mReserve;
        deployed = block.timestamp;
    }

    /// @dev mock fetched data assumes quadratic in time cumulative values
    /// @dev following y = m*t^2 where t is time elapsed since contract
    /// @dev was deployed
    function _fetch() internal virtual override returns (Oracle.Data memory) {
        uint256 priceOverMicroWindow = (getPriceCumulative(block.timestamp) - getPriceCumulative(block.timestamp-microWindow)) / microWindow;
        uint256 priceOverMacroWindow = (getPriceCumulative(block.timestamp) - getPriceCumulative(block.timestamp-macroWindow)) / macroWindow;

        uint256 reservesOverMicroWindow = (getReservesCumulative(block.timestamp) - getReservesCumulative(block.timestamp-microWindow)) / microWindow;
        uint256 reservesOverMacroWindow = (getReservesCumulative(block.timestamp) - getReservesCumulative(block.timestamp-macroWindow)) / macroWindow;

        return Oracle.Data({
            timestamp: block.timestamp,
            microWindow: microWindow,
            macroWindow: macroWindow,
            priceOverMicroWindow: priceOverMicroWindow,
            priceOverMacroWindow: priceOverMacroWindow,
            reservesOverMicroWindow: reservesOverMicroWindow,
            reservesOverMacroWindow: reservesOverMacroWindow
        });
    }

    function getPriceCumulative(uint256 t) public view returns (uint256) {
        uint256 elapsed = t - deployed;
        return mPrice * (elapsed) ** 2;
    }

    function getReservesCumulative(uint256 t) public view returns (uint256) {
        uint256 elapsed = t - deployed;
        return mReserve * (elapsed) ** 2;
    }
}
