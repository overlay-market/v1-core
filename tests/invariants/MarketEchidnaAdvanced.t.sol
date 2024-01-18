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
    event BuildWrapper(bool isLong, uint256 collateral);
    function buildWrapper(bool isLong, uint256 collateral) public {
        // bound collateral to avoid reverts
        collateral = TestUtils.clampBetween(collateral, MIN_COLLATERAL, CAP_NOTIONAL);

        // use the senders specified in the yaml config
        hevm.prank(msg.sender);

        market.build({
            collateral: collateral,
            leverage: 1e18,
            isLong: isLong,
            priceLimit: isLong ? type(uint256).max : 0
        });
    }

    // invariants inherited from base contract
}
