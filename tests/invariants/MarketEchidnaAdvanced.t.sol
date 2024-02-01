// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {MarketEchidna} from "./MarketEchidna.t.sol";
import {TestUtils} from "./TestUtils.sol";

// configure solc-select to use compiler version:
// solc-select install 0.8.10
// solc-select use 0.8.10
//
// run from base project directory with:
// echidna tests/invariants/MarketEchidnaAdvanced.t.sol --contract MarketEchidnaAdvanced --config tests/invariants/MarketEchidnaAdvanced.yaml
contract MarketEchidnaAdvanced is MarketEchidna {
    // wrapper around market.build() to "guide" the fuzz test
    // note: wrappers have to be public in order to be called by Echidna
    function buildWrapper(bool isLong, uint256 collateral) public returns (uint256) {
        // bound collateral to avoid reverts
        collateral = TestUtils.clampBetween(collateral, MIN_COLLATERAL, CAP_NOTIONAL);

        // use the senders specified in the yaml config
        ovl.mint(msg.sender, collateral);
        hevm.prank(msg.sender);

        return market.build({
            collateral: collateral,
            leverage: 1e18,
            isLong: isLong,
            priceLimit: isLong ? type(uint256).max : 0
        });
    }

    // Helper functions

    function _getOiAndShares(bool isLong)
        internal
        view
        returns (uint256 oi, uint256 oiShares)
    {
        oi = isLong ? market.oiLong() : market.oiShort();
        oiShares = isLong ? market.oiLongShares() : market.oiShortShares();
    }

    // Invariants inherited from base contract

    // Invariant 2) Market's oi and oi shares should increase after a build

    function check_oi_after_build(bool isLong, uint256 collateral) public {
        // trigger funding payment so that it doesn't affect the test
        market.update();

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        // build a position
        buildWrapper(isLong, collateral);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter > oiBefore);
        assert(oiSharesAfter > oiSharesBefore);
    }

    // Invariant 3) Market's oi and oi shares should decrease after an unwind

    function check_oi_after_unwind(bool isLong, uint256 collateral) public {
        // build a position
        uint256 posId = buildWrapper(isLong, collateral);

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        // unwind the whole position
        market.unwind(posId, 1e18, isLong ? 0 : type(uint256).max);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter < oiBefore);
        assert(oiSharesAfter < oiSharesBefore);
    }

    // Invariant 4) Market's oi and oi shares should decrease after a liquidation

    function check_oi_after_liquidate(bool isLong, uint256 collateral) public {
        // build a position
        uint256 posId = buildWrapper(isLong, collateral);

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        // adjust the price so that position becomes liquidatable
        uint256 originalPrice = feed.price();
        feed.setPrice(isLong ? originalPrice / 2 : originalPrice * 2);

        // liquidate the position
        market.liquidate(msg.sender, posId);

        // reset the price to keep the test environment consistent
        feed.setPrice(originalPrice);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter < oiBefore);
        assert(oiSharesAfter < oiSharesBefore);
    }
}
