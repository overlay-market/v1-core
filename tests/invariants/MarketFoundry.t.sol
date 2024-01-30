// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {OverlayV1Token} from "../../contracts/OverlayV1Token.sol";
import {OverlayV1FeedFactoryMock} from "../../contracts/mocks/OverlayV1FeedFactoryMock.sol";
import {GOVERNOR_ROLE, MINTER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {TestUtils} from "./TestUtils.sol";

// run from base project directory with:
// forge test --mc MarketFoundry
//
// Reference: https://github.com/overlay-market/v1-core/blob/main/tests/markets/conftest.py
contract MarketFoundry is Test {
    // contracts required for test
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Token ovl;

    // make these constant to match Echidna config
    address public constant ALICE = address(0x1000000000000000000000000000000000000000);
    address public constant BOB = address(0x2000000000000000000000000000000000000000);

    uint256 constant MIN_COLLATERAL = 1e14;
    uint256 constant CAP_NOTIONAL = 8e23;

    function setUp() public virtual {
        // foundry-specific sender setup
        targetSender(ALICE);
        targetSender(BOB);

        // create contracts to be tested
        ovl = new OverlayV1Token();
        factory = new OverlayV1Factory(address(ovl), address(0x111));
        // market will be later deployed by factory

        // ovl config
        uint256 ovlSupply = 8_000_000e18;
        ovl.grantRole(MINTER_ROLE, address(this));
        ovl.mint(address(this), ovlSupply);
        ovl.renounceRole(MINTER_ROLE, address(this));
        ovl.transfer(ALICE, ovlSupply / 2);
        ovl.transfer(BOB, ovlSupply / 2);

        // factory config
        ovl.grantRole(GOVERNOR_ROLE, address(this));
        ovl.grantRole(bytes32(0x00), address(factory)); // grant admin role
        OverlayV1FeedFactoryMock feedFactory =
            new OverlayV1FeedFactoryMock({_microWindow: 600, _macroWindow: 1800});
        factory.addFeedFactory(address(feedFactory));

        // market config and deployment
        address feed = feedFactory.deployFeed({price: 1e29, reserve: 2_000_000e18});
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
            250 // averageBlockTime // FIXME: this will be different in Arbitrum
        ];
        market = OverlayV1Market(factory.deployMarket(address(feedFactory), feed, params));
        vm.prank(ALICE);
        ovl.approve(address(market), ovlSupply / 2);
        vm.prank(BOB);
        ovl.approve(address(market), ovlSupply / 2);
    }

    // Invariant 1) `oiOverweight * oiUnderweight` remains constant after funding payments
    function invariant_oi_product_after_funding() public {
        uint256 lastUpdate = market.timestampUpdateLast();
        uint256 oiLong = market.oiLong();
        uint256 oiShort = market.oiShort();
        uint256 oiOverweightBefore = oiLong > oiShort ? oiLong : oiShort;
        uint256 oiUnderweightBefore = oiLong > oiShort ? oiShort : oiLong;

        uint256 oiProductBefore = oiOverweightBefore * oiUnderweightBefore;

        (uint256 oiOverweightAfter, uint256 oiUnderweightAfter) = market.oiAfterFunding({
            oiOverweight: oiOverweightBefore,
            oiUnderweight: oiUnderweightBefore,
            // FIXME: block.timestamp is always 0 in the test
            // timeElapsed: block.timestamp - lastUpdate
            timeElapsed: 1
        });

        uint256 oiProductAfter = oiOverweightAfter * oiUnderweightAfter;

        emit log_named_uint("oiProductBefore:", oiProductBefore);
        emit log_named_uint("oiProductAfter:", oiProductAfter);

        // 0.1% tolerance
        assert(TestUtils.isApproxEqRel(oiProductBefore, oiProductAfter, 0.1e16));

        // avoid Foundry specific assertions, so we can use this test in Echidna
        // assertApproxEqRel(oiProductBefore, oiProductAfter, 0.1e16, "oi invariant broken");
    }

    function test_break_oi_invariant() public {
        // before the first build, both oi's are 0
        vm.startPrank(ALICE);

        market.build({
            collateral: 9e18,
            leverage: 1e18,
            isLong: true,
            priceLimit: type(uint256).max
        });

        market.build({collateral: 99e18, leverage: 1e18, isLong: false, priceLimit: 0});

        emit log_named_uint("oiLong before funding", market.oiLong());
        emit log_named_uint("oiShort before funding", market.oiShort());
        uint256 oiProductBefore = market.oiShort() * market.oiLong();
        emit log_named_uint("oi product before funding", oiProductBefore);

        (uint256 oiOverweight, uint256 oiUnderweight) = market.oiAfterFunding({
            oiOverweight: market.oiShort(),
            oiUnderweight: market.oiLong(),
            timeElapsed: 1
        });

        emit log_named_uint("oiLong after funding", oiUnderweight);
        emit log_named_uint("oiShort after funding", oiOverweight);
        uint256 oiProductAfter = oiOverweight * oiUnderweight;
        emit log_named_uint("oi product after funding", oiProductAfter);

        // 0.0001% tolerance
        assertApproxEqRel(oiProductBefore, oiProductAfter, 0.0001e16, "oi invariant broken");
    }
}
