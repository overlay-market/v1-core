// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {BaseChainlinkFeedTest} from "./BaseChainlinkFeedTest.sol";
import {OverlayV1Feed} from "contracts/feeds/OverlayV1Feed.sol";
import {OverlayV1ChainlinkFeed} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import {OverlayV1ChainlinkFeedFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";
import "contracts/libraries/Oracle.sol";

/**
 * @title OverlayV1ChainlinkFeedTest
 * @notice Tests for the original V1 Chainlink feed implementation
 */
contract OverlayV1ChainlinkFeedTest is BaseChainlinkFeedTest {
    OverlayV1ChainlinkFeedFactory feedFactory;

    /**
     * @dev Create the V1 feed implementation
     */
    function createFeed(address _aggregator, address _ovl, uint256 _heartbeat)
        internal
        override
        returns (OverlayV1Feed)
    {
        feedFactory = new OverlayV1ChainlinkFeedFactory(_ovl, MICRO_WINDOW, MACRO_WINDOW);
        return OverlayV1Feed(feedFactory.deployFeed(_aggregator, _heartbeat));
    }

    /**
     * @dev Test setting the heartbeat for V1 implementation
     */
    function testSetHeartbeat() public override {
        vm.startPrank(GOVERNOR);

        OverlayV1ChainlinkFeed v1Feed = OverlayV1ChainlinkFeed(address(feed));
        v1Feed.setHeartbeat(120 minutes);

        vm.stopPrank();
        aggregator.setData(1, 105);

        skip(119 minutes);
        feed.latest();

        vm.startPrank(GOVERNOR);

        v1Feed.setHeartbeat(30 minutes);

        vm.stopPrank();

        skip(61 minutes);
        vm.expectRevert("stale price feed");
        feed.latest();

        vm.expectRevert();
        v1Feed.setHeartbeat(60 minutes);
    }

    /**
     * @dev Test price dynamics with decreasing prices
     */
    function testV1DecreasingPrices() public {
        // Set initial price
        aggregator.setData(1, 10e8);
        skip(3600);

        // Now set a lower price
        aggregator.setData(2, 8e8);
        skip(300); // Half of microWindow

        Oracle.Data memory data = feed.latest();

        // Calculate expected microWindow price - in V1 this is just the raw TWAP
        uint256 expectedMicroPriceRaw = (10e18 * 300 + 8e18 * 300) / 600; // Approx 9e18

        // V1 doesn't modify the microWindow price based on its relation to macroWindow
        assertApproxEqRel(data.priceOverMicroWindow, expectedMicroPriceRaw, 1e14);
    }

    /**
     * @dev Test price dynamics with increasing prices
     */
    function testV1IncreasingPrices() public {
        // Set initial price
        aggregator.setData(1, 10e8);
        skip(3600);

        // Now set a higher price
        aggregator.setData(2, 12e8);
        skip(300); // Half of microWindow

        Oracle.Data memory data = feed.latest();

        // Calculate expected microWindow price - in V1 this is just the raw TWAP
        uint256 expectedMicroPriceRaw = (10e18 * 300 + 12e18 * 300) / 600; // Approx 11e18

        // V1 doesn't modify the microWindow price based on its relation to macroWindow
        assertApproxEqRel(data.priceOverMicroWindow, expectedMicroPriceRaw, 1e14);
    }
}
