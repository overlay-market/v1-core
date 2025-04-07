// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";
import "contracts/libraries/Oracle.sol";
import {OverlayV1Feed} from "contracts/feeds/OverlayV1Feed.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";

/**
 * @title BaseChainlinkFeedTest
 * @notice Base contract for testing Chainlink Feed implementations
 * @dev Child contracts must implement the createFeed method to return their specific feed type
 */
abstract contract BaseChainlinkFeedTest is Test {
    AggregatorMock aggregator;
    OverlayV1Feed feed; // Using the base interface type
    OverlayV1Token ovl;
    bytes32 constant GOVERNOR_ROLE = keccak256("GOVERNOR");
    address immutable GOVERNOR = makeAddr("governor");

    // These parameters are shared across all feed implementations
    uint256 constant MICRO_WINDOW = 600; // 10 minutes
    uint256 constant MACRO_WINDOW = 3600; // 1 hour
    uint256 constant DEFAULT_HEARTBEAT = 60 minutes;

    /**
     * @dev Child contracts must implement this method to create the specific feed type
     * @param _aggregator The mock aggregator address
     * @param _ovl The OVL token address
     * @param _heartbeat The heartbeat duration
     * @return The created feed instance
     */
    function createFeed(address _aggregator, address _ovl, uint256 _heartbeat)
        internal
        virtual
        returns (OverlayV1Feed);

    /**
     * @dev Common setup for all feed tests
     */
    function setUp() public virtual {
        vm.createSelectFork(vm.envString("RPC"), 169_490_320);
        ovl = new OverlayV1Token();
        aggregator = new AggregatorMock();
        feed = createFeed(address(aggregator), address(ovl), DEFAULT_HEARTBEAT);
        ovl.grantRole(GOVERNOR_ROLE, GOVERNOR);
    }

    /**
     * @dev Test that the feed reverts when price data is stale
     */
    function testStalePrice() public {
        aggregator.setData(1, 105);

        skip(59 minutes);
        feed.latest();

        aggregator.setData(2, 105);

        skip(61 minutes);
        vm.expectRevert("stale price feed");
        feed.latest();
    }

    /**
     * @dev Test the heartbeat setting functionality
     */
    function testSetHeartbeat() public virtual {
        // This needs to be implemented in child classes as the heartbeat setting
        // is not in OverlayV1Feed somehow. TODO: extract setHeartbeat to OverlayV1Feed
    }

    /**
     * @dev Test basic price calculation consistency
     */
    function testPriceCalculationConsistency() public {
        aggregator.setData(1, 10e8);

        skip(3600);

        Oracle.Data memory stdData = feed.latest();
        assertEq(stdData.priceOverMicroWindow, 10e18);
        assertEq(stdData.priceOverMacroWindow, 10e18);
        assertEq(stdData.priceOneMacroWindowAgo, 0);

        aggregator.setData(2, 12e8);

        skip(3000);

        stdData = feed.latest();

        uint256 microPart = 10 * 600 * 1e18;
        uint256 macroPart = 12 * 3000 * 1e18;
        uint256 expectedMacroPrice = (microPart + macroPart) / 3600;

        uint256 expectedMacroAgoPrice = uint256(10 * 3000 * 1e18) / 3600;

        // The microWindow price calculation varies between implementations,
        // so we test it in the child contracts

        assertApproxEqRel(stdData.priceOverMacroWindow, expectedMacroPrice, 1e14);
        assertApproxEqRel(stdData.priceOneMacroWindowAgo, expectedMacroAgoPrice, 1e14);
    }
}
