// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {MarketEchidna} from "./MarketEchidna.t.sol";
import {TestUtils} from "./TestUtils.sol";

// configure solc-select to use compiler version:
// solc-select install 0.8.10
// solc-select use 0.8.10
//
// run with echidna from base project directory with:
// echidna tests/invariants/MarketEchidnaAdvanced.t.sol --contract MarketEchidnaAdvanced --config tests/invariants/MarketEchidnaAdvanced.yaml
//
// run with medusa from base project directory with:
// medusa fuzz
contract MarketEchidnaAdvanced is MarketEchidna {
    // ghost variables used to verify invariants
    mapping(address => uint256[]) positions; // owner => positionIds

    // same as the ones specified in the fuzzer config
    address[] senders = [ALICE, BOB];

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
        price = TestUtils.clampBetween(price, 1e1, 1e25);
        feed.setPrice(price);
    }

    function unwind(uint256 fraction) public {
        fraction = TestUtils.clampBetween(fraction, 1e14, 1e18);

        uint256[] storage posIds = positions[msg.sender];
        require(posIds.length > 0, "No positions to unwind");
        uint256 posId = posIds[posIds.length - 1];

        (,,,, bool isLong,,,) = market.positions(keccak256(abi.encodePacked(msg.sender, posId)));

        hevm.prank(msg.sender);
        market.unwind(posId, fraction, isLong ? 0 : type(uint256).max);

        (,,,,,,, uint16 fractionRemaining) =
            market.positions(keccak256(abi.encodePacked(msg.sender, posId)));

        // remove the position if fully unwound
        if (fractionRemaining == 0) posIds.pop();
    }

    function liquidate() public {
        uint256[] storage posIds = positions[msg.sender];
        require(posIds.length > 0, "No positions to liquidate");
        uint256 posId = posIds[posIds.length - 1];

        (,,,, bool isLong,,,) = market.positions(keccak256(abi.encodePacked(msg.sender, posId)));

        // adjust the price so that position becomes liquidatable
        setPrice(isLong ? feed.price() / 2 : feed.price() * 2);

        // liquidate the position
        market.liquidate(msg.sender, posId);

        // remove the liquidated position
        posIds.pop();
    }

    // Helper functions

    function _getOiAndShares(bool isLong) internal view returns (uint256 oi, uint256 oiShares) {
        oi = isLong ? market.oiLong() : market.oiShort();
        oiShares = isLong ? market.oiLongShares() : market.oiShortShares();
    }

    // Invariants inherited from base contract

    // Invariant 2) Market's oi and oi shares should increase after a build

    function check_oi_after_build(bool isLong, uint256 collateral) public {
        // bound collateral here to use in oi calculations
        collateral = TestUtils.clampBetween(collateral, MIN_COLLATERAL, CAP_NOTIONAL);

        // trigger funding payment so that it doesn't affect the test
        market.update();

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        // build a position
        buildWrapper(isLong, collateral);

        // calculate the expected oi and oi shares
        uint256 posOi = collateral * 1e18 / feed.price();
        uint256 posOiShares =
            (oiBefore == 0 || oiSharesBefore == 0) ? posOi : oiSharesBefore * posOi / oiBefore;

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter == oiBefore + posOi);
        assert(oiSharesAfter == oiSharesBefore + posOiShares);

        revert(); // revert state changes during the invariant check
    }

    // Invariant 3) Market's oi and oi shares should decrease after an unwind

    function check_oi_after_unwind(bool isLong, uint256 collateral) public {
        // build a position
        uint256 posId = buildWrapper(isLong, collateral);

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        (,,,,,, uint240 posOiShares,) =
            market.positions(keccak256(abi.encodePacked(msg.sender, posId)));
        uint256 posOi = oiSharesBefore == 0 ? 0 : oiBefore * posOiShares / oiSharesBefore;

        // unwind the whole position
        hevm.prank(msg.sender);
        market.unwind(posId, 1e18, isLong ? 0 : type(uint256).max);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter == oiBefore - posOi);
        assert(oiSharesAfter == oiSharesBefore - posOiShares);

        revert(); // revert state changes during the invariant check
    }

    // Invariant 4) Market's oi and oi shares should decrease after a liquidation

    function check_oi_after_liquidate(bool isLong, uint256 collateral) public {
        // build a position
        uint256 posId = buildWrapper(isLong, collateral);

        (uint256 oiBefore, uint256 oiSharesBefore) = _getOiAndShares(isLong);

        (,,,,,, uint240 posOiShares,) =
            market.positions(keccak256(abi.encodePacked(msg.sender, posId)));
        uint256 posOi = oiSharesBefore == 0 ? 0 : oiBefore * posOiShares / oiSharesBefore;

        // adjust the price so that position becomes liquidatable
        feed.setPrice(isLong ? feed.price() / 2 : feed.price() * 2);

        // liquidate the position (don't need to prank the sender here)
        market.liquidate(msg.sender, posId);

        (uint256 oiAfter, uint256 oiSharesAfter) = _getOiAndShares(isLong);

        assert(oiAfter == oiBefore - posOi);
        assert(oiSharesAfter == oiSharesBefore - posOiShares);

        revert(); // revert state changes during the invariant check
    }

    // Invariant 5) Sum of open position's oi shares should be equal to market's total oi shares

    event InvariantOiSharesSum(
        uint256 numPositions,
        uint256 sumLongExpected,
        uint256 sumLong,
        uint256 sumShortExpected,
        uint256 sumShort
    );

    function check_oi_shares_sum() public {
        uint256 numPositions;
        uint256 sumOiLongShares;
        uint256 sumOiShortShares;

        // iterate over all the senders
        for (uint256 i = 0; i < senders.length; i++) {
            // iterate over all the positions of the sender
            for (uint256 j = 0; j < positions[senders[i]].length; j++) {
                (,,,, bool isLong,, uint240 oiShares,) = market.positions(
                    keccak256(abi.encodePacked(senders[i], positions[senders[i]][j]))
                );

                if (isLong) {
                    sumOiLongShares += oiShares;
                } else {
                    sumOiShortShares += oiShares;
                }

                numPositions++;
            }
        }

        // FIXME: echidna breaks the invariant (parameters are not bounded on this output).
        // check_oi_shares_sum(): failed!💥
        //   Call sequence, shrinking 1675/5000:
        //     buildWrapper(false,0)
        //     unwind(29678335934853632302057079988033485840348142661768149768981112452983)
        //     unwind(7311677140176116913925425463138979182172112599739844530104983646231913891)
        //     check_oi_shares_sum()
        // Event sequence:
        // InvariantOiSharesSum(0, 0, 0, 275, 0)
        //
        // The issue is that, after unwinding a position, its fractionRemaining can be set to 0 (ie. the position is effectively closed) while its oiShares are still greater than 0.
        // Example position: fractionRemaining = 0 ; oiShares = 1.73e12
        emit InvariantOiSharesSum(
            numPositions,
            market.oiLongShares(),
            sumOiLongShares,
            market.oiShortShares(),
            sumOiShortShares
        );

        assert(sumOiLongShares == market.oiLongShares());
        assert(sumOiShortShares == market.oiShortShares());
    }
}
