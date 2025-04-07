// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {BaseChainlinkFeedTest} from "./BaseChainlinkFeedTest.sol";
import {OverlayV1Feed} from "contracts/feeds/OverlayV1Feed.sol";
import {OverlayV1ChainlinkFeedZero} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeedZero.sol";
import {OverlayV1ChainlinkFeedZeroFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedZeroFactory.sol";
import "contracts/libraries/Oracle.sol";
import {console2} from "forge-std/Test.sol";

/**
 * @title OverlayV1ChainlinkFeedZeroTest
 * @notice Tests for the Zero variant of Chainlink feed with protection against frontrunning
 */
contract OverlayV1ChainlinkFeedZeroTest is BaseChainlinkFeedTest {
    OverlayV1ChainlinkFeedZeroFactory feedFactory;

    /**
     * @dev Create the Zero feed implementation
     */
    function createFeed(address _aggregator, address _ovl, uint256 _heartbeat)
        internal
        override
        returns (OverlayV1Feed)
    {
        feedFactory = new OverlayV1ChainlinkFeedZeroFactory(_ovl, MICRO_WINDOW, MACRO_WINDOW);
        return OverlayV1Feed(feedFactory.deployFeed(_aggregator, _heartbeat));
    }

    /**
     * @dev Test setting the heartbeat for Zero implementation
     */
    function testSetHeartbeat() public override {
        vm.startPrank(GOVERNOR);

        OverlayV1ChainlinkFeedZero zeroFeed = OverlayV1ChainlinkFeedZero(address(feed));
        zeroFeed.setHeartbeat(120 minutes);

        vm.stopPrank();
        aggregator.setData(1, 105);

        skip(119 minutes);
        feed.latest();

        vm.startPrank(GOVERNOR);

        zeroFeed.setHeartbeat(30 minutes);

        vm.stopPrank();

        skip(61 minutes);
        vm.expectRevert("stale price feed");
        feed.latest();

        vm.expectRevert();
        zeroFeed.setHeartbeat(60 minutes);
    }

    /**
     * @dev Test Zero-specific price calculation logic
     */
    function testZeroMicroWindowPriceCalculation() public {
        aggregator.setData(1, 10e8);
        skip(3600);

        aggregator.setData(2, 12e8);
        skip(3000);

        Oracle.Data memory data = feed.latest();

        // In Zero variant, microWindow price should be max(spot, microWindow)
        // since macroWindow < microWindow (price is increasing)
        uint256 expectedSpotPrice = 12 * 1e18;
        assertEq(data.priceOverMicroWindow, expectedSpotPrice, "Should select spot price");
    }

    // Test when macroWindow price > microWindow price (price is decreasing)
    function testMacroGreaterThanMicro() public {
        // Set initial price
        aggregator.setData(1, 10e8);
        skip(3600);

        // Now set a lower price
        aggregator.setData(2, 8e8);
        skip(300); // Half of microWindow

        Oracle.Data memory data = feed.latest();

        uint256 expectedSpotPrice = 8e18;

        // Calculate expected microWindow price without adjustment
        uint256 expectedMicroPriceRaw = uint256(10e18 * 300 + 8e18 * 300) / 600; // Approx 9e18
        uint256 expectedMacroPrice = uint256(10e18 * 3300 + 8e18 * 300) / 3600; // Close to 9.8e18

        // Log values for debugging
        console2.log("Macro Price:", expectedMacroPrice);
        console2.log("Micro Price Raw:", expectedMicroPriceRaw);
        console2.log("Spot Price:", expectedSpotPrice);
        console2.log("Actual MicroWindow:", data.priceOverMicroWindow);

        // Since macroWindow > microWindow, we expect min(spot, microWindow) = spot = 8e18
        assertTrue(
            expectedMacroPrice > expectedMicroPriceRaw, "Macro should be greater than micro"
        );
        assertEq(data.priceOverMicroWindow, expectedSpotPrice, "Should select min value (spot)");
    }

    // Test when macroWindow price < microWindow price (price is increasing)
    function testMacroLessThanMicro() public {
        // Set initial price
        aggregator.setData(1, 10e8);
        skip(3600);

        // Now set a higher price
        aggregator.setData(2, 12e8);
        skip(300); // Half of microWindow

        Oracle.Data memory data = feed.latest();

        uint256 expectedSpotPrice = 12e18;

        // Calculate expected microWindow price without adjustment
        uint256 expectedMicroPriceRaw = uint256(10e18 * 300 + 12e18 * 300) / 600; // Approx 11e18
        uint256 expectedMacroPrice = uint256(10e18 * 3300 + 12e18 * 300) / 3600; // Close to 10.2e18

        // Log values for debugging
        console2.log("Macro Price:", expectedMacroPrice);
        console2.log("Micro Price Raw:", expectedMicroPriceRaw);
        console2.log("Spot Price:", expectedSpotPrice);
        console2.log("Actual MicroWindow:", data.priceOverMicroWindow);

        // Since macroWindow < microWindow, we expect max(spot, microWindow) = spot = 12e18
        assertTrue(expectedMacroPrice < expectedMicroPriceRaw, "Macro should be less than micro");
        assertEq(data.priceOverMicroWindow, expectedSpotPrice, "Should select max value (spot)");
    }

    // Test extreme price movement - price crash (90% drop)
    function testExtremePriceCrash() public {
        // Set initial price
        aggregator.setData(1, 100e8);
        skip(3600);

        // Now simulate a crash (90% drop)
        aggregator.setData(2, 10e8);
        skip(300); // Half of microWindow

        Oracle.Data memory data = feed.latest();

        uint256 expectedSpotPrice = 10e18;
        uint256 expectedMicroPriceRaw = (100e18 * 300 + 10e18 * 300) / 600; // Approx 55e18
        uint256 expectedMacroPrice = (100e18 * 3300 + 10e18 * 300) / 3600; // Close to 92e18

        console2.log("Macro Price:", expectedMacroPrice);
        console2.log("Micro Price Raw:", expectedMicroPriceRaw);
        console2.log("Spot Price:", expectedSpotPrice);
        console2.log("Actual MicroWindow:", data.priceOverMicroWindow);

        // Since macroWindow > microWindow, we expect min(spot, microWindow) = spot = 10e18
        assertTrue(
            expectedMacroPrice > expectedMicroPriceRaw, "Macro should be greater than micro"
        );
        assertEq(data.priceOverMicroWindow, expectedSpotPrice, "Should select min value (spot)");
    }

    // Test extreme price movement - price spike (10x)
    function testExtremePriceSpike() public {
        // Set initial price
        aggregator.setData(1, 10e8);
        skip(3600);

        // Now simulate a spike (10x)
        aggregator.setData(2, 100e8);
        skip(300); // Half of microWindow

        Oracle.Data memory data = feed.latest();

        uint256 expectedSpotPrice = 100e18;
        uint256 expectedMicroPriceRaw = (10e18 * 300 + 100e18 * 300) / 600; // Approx 55e18
        uint256 expectedMacroPrice = (10e18 * 3300 + 100e18 * 300) / 3600; // Close to 18e18

        console2.log("Macro Price:", expectedMacroPrice);
        console2.log("Micro Price Raw:", expectedMicroPriceRaw);
        console2.log("Spot Price:", expectedSpotPrice);
        console2.log("Actual MicroWindow:", data.priceOverMicroWindow);

        // Since macroWindow < microWindow, we expect max(spot, microWindow) = spot = 100e18
        assertTrue(expectedMacroPrice < expectedMicroPriceRaw, "Macro should be less than micro");
        assertEq(data.priceOverMicroWindow, expectedSpotPrice, "Should select max value (spot)");
    }
}
