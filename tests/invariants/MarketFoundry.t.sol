// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "../../contracts/OverlayV1Factory.sol";
import "../../contracts/OverlayV1Market.sol";
import "../../contracts/OverlayV1Token.sol";

// run from base project directory with:
// forge test --mc MarketFoundry
contract MarketFoundry {

    // contracts required for test
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Token ovl;

    function setUp() public {
        // create contracts to be tested
        ovl = new OverlayV1Token();
    }

    function invariant_ovl_decimals() public view {
        assert(ovl.decimals() == 18);
    }

}
