// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {OverlayV1Token} from "../../contracts/OverlayV1Token.sol";
import {OverlayV1FeedFactoryMock} from "../../contracts/mocks/OverlayV1FeedFactoryMock.sol";
import {OverlayV1FeedMock} from "../../contracts/mocks/OverlayV1FeedMock.sol";
import {GOVERNOR_ROLE, MINTER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {TestUtils} from "./TestUtils.sol";

// Reference: https://github.com/crytic/building-secure-contracts/blob/master/program-analysis/echidna/advanced/on-using-cheat-codes.md
interface IHevm {
    function prank(address) external;
}

// configure solc-select to use compiler version:
// solc-select install 0.8.10
// solc-select use 0.8.10
//
// run from base project directory with:
// echidna tests/invariants/MarketEchidna.t.sol --contract MarketEchidna --config tests/invariants/MarketEchidna.yaml
//
// Reference: https://github.com/overlay-market/v1-core/blob/main/tests/markets/conftest.py
contract MarketEchidna {
    IHevm hevm = IHevm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    // contracts required for test
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Token ovl;
    OverlayV1FeedMock feed;

    // make these constant to match Echidna config
    address constant ALICE = address(0x1000000000000000000000000000000000000000);
    address constant BOB = address(0x2000000000000000000000000000000000000000);

    uint256 constant MIN_COLLATERAL = 1e14;
    uint256 constant CAP_NOTIONAL = 8e23;

    constructor() {
        // create contracts to be tested
        ovl = new OverlayV1Token();
        factory = new OverlayV1Factory(address(ovl), address(0x111));
        // market will be later deployed by factory

        // ovl config; fund test accounts
        ovl.grantRole(MINTER_ROLE, address(this));
        ovl.mint(ALICE, 4_000_000e18);
        ovl.mint(BOB, 4_000_000e18);

        // factory config
        ovl.grantRole(GOVERNOR_ROLE, address(this));
        ovl.grantRole(bytes32(0x00), address(factory)); // grant admin role
        OverlayV1FeedFactoryMock feedFactory =
            new OverlayV1FeedFactoryMock({_microWindow: 600, _macroWindow: 1800});
        factory.addFeedFactory(address(feedFactory));

        // market config and deployment
        feed = OverlayV1FeedMock(feedFactory.deployFeed({price: 1e29, reserve: 2_000_000e18}));
        uint256[15] memory params = [
            uint256(122000000000), // k
            500000000000000000, // lmbda
            2500000000000000, // delta
            5000000000000000000, // capPayoff
            CAP_NOTIONAL, // capNotional
            5000000000000000000, // capLeverage
            2592000, // circuitBreakerWindow
            66670000000000000000000, // circuitBreakerMintTarget
            100000000000000000, // maintenanceMargin
            100000000000000000, // maintenanceMarginBurnRate
            50000000000000000, // liquidationFeeRate
            750000000000000, // tradingFeeRate
            MIN_COLLATERAL, // minCollateral
            25000000000000, // priceDriftUpperLimit
            250 // averageBlockTime
        ];
        market = OverlayV1Market(factory.deployMarket(address(feedFactory), address(feed), params));
        hevm.prank(ALICE);
        ovl.approve(address(market), type(uint256).max);
        hevm.prank(BOB);
        ovl.approve(address(market), type(uint256).max);
    }

    // Invariant 1) `oiOverweight * oiUnderweight` remains constant after funding payments

    // event to raise if the invariant is broken
    event OiAfterFunding(uint256 oiProductBefore, uint256 oiProductAfter);

    function check_oi_product_after_funding(uint256 timeElapsed) public {
        uint256 oiLong = market.oiLong();
        uint256 oiShort = market.oiShort();
        uint256 oiOverweightBefore = oiLong > oiShort ? oiLong : oiShort;
        uint256 oiUnderweightBefore = oiLong > oiShort ? oiShort : oiLong;

        uint256 oiProductBefore = oiOverweightBefore * oiUnderweightBefore;

        (uint256 oiOverweightAfter, uint256 oiUnderweightAfter) = market.oiAfterFunding({
            oiOverweight: oiOverweightBefore,
            oiUnderweight: oiUnderweightBefore,
            timeElapsed: timeElapsed
        });

        uint256 oiProductAfter = oiOverweightAfter * oiUnderweightAfter;

        // only visible when invariant fails
        emit OiAfterFunding(oiProductBefore, oiProductAfter);

        // 0.5% tolerance
        assert(TestUtils.isApproxEqRel(oiProductBefore, oiProductAfter, 0.5e16));
    }
}
