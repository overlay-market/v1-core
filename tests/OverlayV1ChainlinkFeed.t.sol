// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";
import {OverlayV1ChainlinkFeed} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import {OverlayV1ChainlinkFeedFactory} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";

contract MarketTest is Test {
    AggregatorMock aggregator;
    OverlayV1ChainlinkFeed feed;
    OverlayV1ChainlinkFeedFactory feedFactory;

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC"), 169_490_320);

        aggregator = new AggregatorMock();
        feedFactory = new OverlayV1ChainlinkFeedFactory(600, 3600);
        feed = OverlayV1ChainlinkFeed(feedFactory.deployFeed(address(aggregator), 60 minutes));

    }

    function testStalePrice() public{
        aggregator.setData(1, 105);

        skip(59 minutes);
        feed.latest();

        aggregator.setData(2, 105);

        skip(61 minutes);
        vm.expectRevert("stale price feed");
        feed.latest();
    }
}
