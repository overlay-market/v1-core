// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../libraries/Oracle.sol";
import "../feeds/OverlayV1Feed.sol";

contract OverlayV1FeedMock is OverlayV1Feed {
    uint256 immutable public price;
    uint256 immutable public reserves;

    constructor(
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _price,
        uint256 _reserves
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        price = _price;
        reserves = _reserves;
    }

    /// @dev mock fetched data assumes values for price, reserve are constant
    function _fetch() internal virtual override returns (Oracle.Data memory) {
        return Oracle.Data({
            timestamp: block.timestamp,
            microWindow: microWindow,
            macroWindow: macroWindow,
            priceOverMicroWindow: price,
            priceOverMacroWindow: price,
            reservesOverMicroWindow: reserves,
            reservesOverMacroWindow: reserves
        });
    }
}
