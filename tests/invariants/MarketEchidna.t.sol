// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../../contracts/OverlayV1Factory.sol";
import "../../contracts/OverlayV1Market.sol";
import "../../contracts/OverlayV1Token.sol";

// configure solc-select to use compiler version:
// solc-select install 0.8.10
// solc-select use 0.8.10
//
// run from base project directory with:
// echidna tests/invariants/MarketEchidna.t.sol --contract MarketEchidna --config tests/invariants/MarketEchidna.yaml
contract MarketEchidna {

    // contracts required for test
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Token ovl;

    constructor() {
        // create contracts to be tested
        ovl = new OverlayV1Token();
    }

    function invariant_ovl_decimals() public view returns (bool) {
        return(ovl.decimals() == 18);
    }

}
