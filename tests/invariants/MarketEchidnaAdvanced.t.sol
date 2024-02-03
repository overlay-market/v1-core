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
    // ghost variables used to verify invariants
    mapping(address => uint256[]) positions; // owner => positionIds

    // Handler functions to "guide" the stateful fuzz test
    // Note: handlers have to be public in order to be called by Echidna

    // wrapper around market.build()
    function buildWrapper(bool isLong, uint256 collateral) public returns (uint256 posId) {
        // bound collateral to avoid reverts
        collateral = TestUtils.clampBetween(collateral, MIN_COLLATERAL, CAP_NOTIONAL);

        // use the senders specified in the yaml config
        ovl.mint(msg.sender, collateral);
        hevm.prank(msg.sender);

        posId = market.build({
            collateral: collateral,
            leverage: 1e18,
            isLong: isLong,
            priceLimit: isLong ? type(uint256).max : 0
        });

        // save positions built by the sender to use in other handlers
        positions[msg.sender].push(posId);
    }

    function setPrice(uint256 price) public {
        // bound market price to a reasonable range
        price = TestUtils.clampBetween(price, 1, 1e29);
        feed.setPrice(price);
    }

    function unwind(uint256 fraction) public {
        fraction = TestUtils.clampBetween(fraction, 1e14, 1e18);

        uint256[] storage posIds = positions[msg.sender];
        require(posIds.length > 0, "No positions to unwind");
        uint256 posId = posIds[posIds.length - 1];

        (,,,,bool isLong,,,) = market.positions(keccak256(abi.encodePacked(msg.sender, posId)));

        hevm.prank(msg.sender);
        market.unwind(posId, fraction, isLong ? 0 : type(uint256).max);

        (,,,,,,,uint16 fractionRemaining) = market.positions(keccak256(abi.encodePacked(msg.sender, posId)));

        // remove the position if fully unwound
        if (fractionRemaining == 0) posIds.pop();
    }

    function liquidate() public {
        uint256[] storage posIds = positions[msg.sender];
        require(posIds.length > 0, "No positions to unwind");
        uint256 posId = posIds[posIds.length - 1];

        (,,,,bool isLong,,,) = market.positions(keccak256(abi.encodePacked(msg.sender, posId)));

        // adjust the price so that position becomes liquidatable
        setPrice(isLong ? feed.price() / 2 : feed.price() * 2);

        // liquidate the position
        market.liquidate(msg.sender, posId);

        // remove the liquidated position
        posIds.pop();
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

        revert(); // revert state changes during the invariant check
    }

    // Invariant 3) Market's oi and oi shares should decrease after an unwind

    function check_oi_after_unwind(bool isLong, uint256 collateral) public {
        // build a position
        uint256 posId = buildWrapper(isLong, collateral);

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        // unwind the whole position
        hevm.prank(msg.sender);
        market.unwind(posId, 1e18, isLong ? 0 : type(uint256).max);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter < oiBefore);
        assert(oiSharesAfter < oiSharesBefore);

        revert(); // revert state changes during the invariant check
    }

    // Invariant 4) Market's oi and oi shares should decrease after a liquidation

    function check_oi_after_liquidate(bool isLong, uint256 collateral) public {
        // build a position
        uint256 posId = buildWrapper(isLong, collateral);

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        // adjust the price so that position becomes liquidatable
        feed.setPrice(isLong ? feed.price() / 2 : feed.price() * 2);

        // liquidate the position (don't need to prank the sender here)
        market.liquidate(msg.sender, posId);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter < oiBefore);
        assert(oiSharesAfter < oiSharesBefore);

        revert(); // revert state changes during the invariant check
    }
}
