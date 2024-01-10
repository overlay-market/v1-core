// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {MarketEchidna} from "./MarketEchidna.t.sol";

// configure solc-select to use compiler version:
// solc-select install 0.8.10
// solc-select use 0.8.10
//
// run from base project directory with:
// echidna tests/invariants/MarketEchidnaAdvanced.t.sol --contract MarketEchidnaAdvanced --config tests/invariants/MarketEchidnaAdvanced.yaml
contract MarketEchidnaAdvanced is MarketEchidna {

    // wrapper around market.build() to "guide" the fuzz test
    function buildWrapper(bool isLong, uint256 collateral) public {
        hevm.prank(msg.sender); // use the senders specified in the yaml config

        market.build({
            collateral: collateral,
            leverage: 1e18,
            isLong: isLong,
            priceLimit: isLong ? type(uint256).max : 0
        });
    }

    // invariants inherited from base contract
}
