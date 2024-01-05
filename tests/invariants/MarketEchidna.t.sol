// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {OverlayV1Token} from "../../contracts/OverlayV1Token.sol";
import {OverlayV1FeedFactoryMock} from "../../contracts/mocks/OverlayV1FeedFactoryMock.sol";
import {GOVERNOR_ROLE, MINTER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";

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
    IHevm hevm = IHevm(address(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D));

    // contracts required for test
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Token ovl;

    // make these constant to match Echidna config
    address public constant ALICE = address(0x1000000000000000000000000000000000000000);
    address public constant BOB = address(0x2000000000000000000000000000000000000000);

    constructor() {
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
        OverlayV1FeedFactoryMock feedFactory = new OverlayV1FeedFactoryMock({
            _microWindow: 600,
            _macroWindow: 1800
        });
        factory.addFeedFactory(address(feedFactory));

        // market config and deployment
        address feed = feedFactory.deployFeed({
            price: 1e18, // TODO: try more extreme prices
            reserve: 2_000_000e18
        });
        uint256[15] memory params = [
            uint256(122000000000),  // k
            500000000000000000,  // lmbda
            2500000000000000,  // delta
            5000000000000000000,  // capPayoff
            800000000000000000000000,  // capNotional
            5000000000000000000,  // capLeverage
            2592000,  // circuitBreakerWindow
            66670000000000000000000,  // circuitBreakerMintTarget
            100000000000000000,  // maintenanceMargin
            100000000000000000,  // maintenanceMarginBurnRate
            50000000000000000,  // liquidationFeeRate
            750000000000000,  // tradingFeeRate
            100000000000000,  // minCollateral
            25000000000000,  // priceDriftUpperLimit
            12 // averageBlockTime // FIXME: this will be different in Arbitrum
        ];
        market = OverlayV1Market(factory.deployMarket(address(feedFactory), feed, params));
    }

    // Invariant 1) `oiOverweight * oiUnderweight` remains constant after funding payments
    function invariant_oi_product_after_funding() public view returns (bool) {
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

        return(oiProductBefore == oiProductAfter);
    }

}
