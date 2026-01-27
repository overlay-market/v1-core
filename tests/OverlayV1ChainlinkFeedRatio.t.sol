// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {BaseChainlinkFeedTest} from "./BaseChainlinkFeedTest.sol";
import {OverlayV1Feed} from "contracts/feeds/OverlayV1Feed.sol";
import {OverlayV1ChainlinkFeedRatio} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeedRatio.sol";
import {OverlayV1ChainlinkFeedRatioFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedRatioFactory.sol";
import "contracts/libraries/Oracle.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";
import {console2} from "forge-std/Test.sol";


/**
 * @title OverlayV1ChainlinkFeedRatioTest
 * @notice Tests for the Ratio variant of Chainlink feed with protection against frontrunning
 */
contract OverlayV1ChainlinkFeedRatioTest is BaseChainlinkFeedTest {
    OverlayV1ChainlinkFeedRatioFactory feedFactory;
    AggregatorMock aggregatorQuote;

    /**
     * @dev Create the Ratio feed implementation
     */
    function createFeed(address _aggregator, address _ovl, uint256 _heartbeat)
        internal
        override
        returns (OverlayV1Feed)
    {
        feedFactory = new OverlayV1ChainlinkFeedRatioFactory(_ovl, MICRO_WINDOW, MACRO_WINDOW);
        aggregatorQuote = new AggregatorMock();

        // Setup base & quote history to avoid !macroAgo reverts
        uint256 finalTime = block.timestamp;
        vm.warp(finalTime - 100 days);
        aggregator.setData(1, 10e8);
        aggregatorQuote.setData(1, 1e8);
        vm.warp(finalTime);
        aggregator.setData(2, 10e8);
        aggregatorQuote.setData(2, 1e8);

        return OverlayV1Feed(feedFactory.deployFeed(address(aggregator), address(aggregatorQuote), _heartbeat));
    }


    /**
     * @dev Test setting the heartbeat for Ratio implementation
     */
    function testSetHeartbeat() public override {
        vm.startPrank(GOVERNOR);

        OverlayV1ChainlinkFeedRatio ratioFeed = OverlayV1ChainlinkFeedRatio(address(feed));
        ratioFeed.setHeartbeat(120 minutes);

        vm.stopPrank();
        aggregator.setData(3, 105e8);
        aggregatorQuote.setData(3, 1e8);

        skip(119 minutes);
        feed.latest();

        vm.startPrank(GOVERNOR);

        ratioFeed.setHeartbeat(30 minutes);

        vm.stopPrank();

        skip(61 minutes);
        vm.expectRevert("OVLV1: !base stale");
        feed.latest();

        vm.expectRevert();
        ratioFeed.setHeartbeat(60 minutes);
    }

    /**
     * @dev Test ratio price calculation
     */
    function testRatioPriceCalculation() public {
        // Base price = 100, Quote price = 2
        // Ratio should be 50
        aggregator.setData(3, 100e8);
        aggregatorQuote.setData(3, 2e8);
        skip(3600);

        aggregator.setData(4, 100e8);
        aggregatorQuote.setData(4, 2e8);

        Oracle.Data memory data = feed.latest();
        assertEq(data.priceOverMicroWindow, 50e18);
        assertEq(data.priceOverMacroWindow, 50e18);

    }

    /**
     * @dev Test that the feed reverts when price data is stale
     */
    function testStalePrice() public override {
        aggregator.setData(3, 10e8);
        // Don't overwrite aggregatorQuote round 1/2 to keep history
        aggregatorQuote.setData(3, 1e8);

        skip(DEFAULT_HEARTBEAT - 1);
        feed.latest();

        // Test base stale
        skip(2);
        vm.expectRevert("OVLV1: !base stale");
        feed.latest();

        // Update base, now quote should be stale
        aggregator.setData(4, 10e8);
        // We need to skip more to make quote stale
        skip(DEFAULT_HEARTBEAT);
        // Update base again to keep it fresh
        aggregator.setData(5, 10e8);
        vm.expectRevert("OVLV1: !quote stale");
        feed.latest();

        // Update quote, now should be fine
        aggregatorQuote.setData(4, 1e8);
        feed.latest();
    }

    function testPriceCalculationConsistency() public override {
        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);

        skip(3600);

        aggregator.setData(4, 10e8);
        aggregatorQuote.setData(4, 1e8);

        Oracle.Data memory stdData = feed.latest();
        assertEq(stdData.priceOverMicroWindow, 10e18);
        assertEq(stdData.priceOverMacroWindow, 10e18);
        assertEq(stdData.priceOneMacroWindowAgo, 10e18); // Based on createFeed history

        aggregator.setData(5, 12e8);
        aggregatorQuote.setData(5, 1e8);

        skip(3000);

        stdData = feed.latest();

        uint256 microPart = 10 * 600 * 1e18;
        uint256 macroPart = 12 * 3000 * 1e18;
        uint256 expectedMacroPrice = (microPart + macroPart) / 3600;

        uint256 expectedMacroAgoPrice = 10e18; // Window: [T-7200, T-3600] was all at 10

        // The microWindow price calculation varies between implementations,
        // so we test it in the child contracts

        assertApproxEqRel(stdData.priceOverMacroWindow, expectedMacroPrice, 1e14);
        assertApproxEqRel(stdData.priceOneMacroWindowAgo, expectedMacroAgoPrice, 1e14);
    }

    /**
     * @dev Test Ratio-specific price calculation logic
     */
    function testRatioMicroWindowPriceCalculation() public {

        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);
        skip(3600);

        aggregator.setData(4, 12e8);
        aggregatorQuote.setData(4, 1e8);
        skip(3000);

        Oracle.Data memory data = feed.latest();

        // In Ratio variant (same logic as Zero), microWindow price should be max(spot, microWindow)
        // since macroWindow < microWindow (price is increasing)
        uint256 expectedSpotPrice = 12 * 1e18;
        assertEq(data.priceOverMicroWindow, expectedSpotPrice, "Should select spot price");
    }

    // Test when macroWindow price > microWindow price (price is decreasing)
    function testMacroGreaterThanMicro() public {
        // Set initial price
        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);
        skip(3600);

        // Now set a lower price
        aggregator.setData(4, 8e8);
        aggregatorQuote.setData(4, 1e8);
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
        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);
        skip(3600);

        // Now set a higher price
        aggregator.setData(4, 12e8);
        aggregatorQuote.setData(4, 1e8);
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
        aggregator.setData(3, 100e8);
        aggregatorQuote.setData(3, 1e8);
        skip(3600);

        // Now simulate a crash (90% drop)
        aggregator.setData(4, 10e8);
        aggregatorQuote.setData(4, 1e8);
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
        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);
        skip(3600);

        // Now simulate a spike (10x)
        aggregator.setData(4, 100e8);
        aggregatorQuote.setData(4, 1e8);
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

    // Test where the pricing function selects microWindow price instead of spot price
    function testRatioSelectsMicroWindowPrice() public {
        // Set initial price
        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);
        skip(3600);

        // Create a scenario with decreasing price trend
        aggregator.setData(4, 8e8);
        aggregatorQuote.setData(4, 1e8);
        skip(400); // Most of microWindow with price at 8e8

        // Price rebounds quickly at the end of microWindow
        // This creates a situation where spot > microWindow but overall trend is down
        aggregator.setData(5, 9e8);
        aggregatorQuote.setData(5, 1e8);
        skip(200);

        Oracle.Data memory data = feed.latest();

        // Expected values
        // - Spot price is 9e8 (scaled to 9e18)
        // - MicroWindow TWAP is (8e18 * 400 + 9e18 * 200) / 600 = 8.33e18
        // - MacroWindow is close to 10e18 with a bit of lower prices

        uint256 expectedSpotPrice = 9e18;
        uint256 expectedMicroPrice = uint256(8e18 * 400 + 9e18 * 200) / 600; // ~8.33e18

        console2.log("Macro Price:", data.priceOverMacroWindow);
        console2.log("Micro Price Raw:", expectedMicroPrice);
        console2.log("Spot Price:", expectedSpotPrice);
        console2.log("Actual MicroWindow:", data.priceOverMicroWindow);

        // Since overall trend is down (macro > micro), result should be min(spot, micro) = micro
        assertTrue(
            data.priceOverMacroWindow > expectedMicroPrice, "Macro should be greater than micro"
        );
        assertTrue(
            expectedSpotPrice > data.priceOverMicroWindow, "Result should be less than spot price"
        );
        assertApproxEqRel(
            data.priceOverMicroWindow, expectedMicroPrice, 1e14, "Should select microWindow price"
        );
    }

    // Test for the case when macroWindow equals microWindow
    function testWhenMacroEqualsMicro() public {
        // Set initial price
        aggregator.setData(3, 10e8);
        aggregatorQuote.setData(3, 1e8);

        // We'll update the price at regular intervals
        // This ensures we don't trigger the stale price feed check
        for (uint256 i = 0; i < 12; i++) {
            skip(600); // Skip 10 minutes at a time
            // Update the price with the same value but advancing the timestamp
            aggregator.setData(uint80(4 + i), int256(10e8));
            aggregatorQuote.setData(uint80(4 + i), int256(1e8));
        }

        // Confirm that macro and micro are equal
        Oracle.Data memory initialData = feed.latest();
        assertApproxEqRel(
            initialData.priceOverMacroWindow,
            initialData.priceOverMicroWindow,
            1e14,
            "Macro and micro should be equal initially"
        );

        console2.log("Initial Macro Price:", initialData.priceOverMacroWindow);
        console2.log("Initial Micro Price:", initialData.priceOverMicroWindow);

        // Now set a different spot price
        int256 newSpotPrice = 12e8; // Different than the TWAP values
        aggregator.setData(uint80(16), newSpotPrice);
        aggregatorQuote.setData(uint80(16), 1e8);

        // Get the latest data
        Oracle.Data memory data = feed.latest();

        // Expected values - cast the spot price to uint256 for calculations
        uint256 expectedSpotPrice =
            uint256(newSpotPrice) * 10 ** (18 - uint256(aggregator.decimals())); // 12e18

        console2.log("Macro Price:", data.priceOverMacroWindow);
        console2.log("Micro Price from TWAPs:", data.priceOverMacroWindow); // Should be mostly the same as macro still
        console2.log("Spot Price:", expectedSpotPrice);
        console2.log("Actual Micro Window:", data.priceOverMicroWindow);

        // With our new equality condition, when macro == micro, the result should be spot price
        assertApproxEqRel(
            data.priceOverMacroWindow,
            initialData.priceOverMacroWindow,
            1e14,
            "Macro window should still be approximately the same"
        );

        // The key test: when macro equals micro, the result should be the spot price
        // regardless of whether it's higher or lower
        assertApproxEqRel(
            data.priceOverMicroWindow,
            expectedSpotPrice,
            1e14,
            "When macro equals micro, result should be spot price"
        );
    }
}
