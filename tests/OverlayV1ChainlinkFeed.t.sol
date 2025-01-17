// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";
import {OverlayV1ChainlinkFeed} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import {OverlayV1ChainlinkFeedFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";

contract MarketTest is Test {
    AggregatorMock aggregator;
    OverlayV1ChainlinkFeed feed;
    OverlayV1ChainlinkFeedFactory feedFactory;
    OverlayV1Token ovl;
    bytes32 constant GOVERNOR_ROLE = keccak256("GOVERNOR");
    address immutable GOVERNOR = makeAddr("governor");

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC"), 169_490_320);
        ovl = new OverlayV1Token();
        aggregator = new AggregatorMock();
        feedFactory = new OverlayV1ChainlinkFeedFactory(address(ovl), 600, 3600);
        feed = OverlayV1ChainlinkFeed(feedFactory.deployFeed(address(aggregator), 60 minutes));
        ovl.grantRole(GOVERNOR_ROLE, GOVERNOR);
    }

    function testStalePrice() public {
        aggregator.setData(1, 105);

        skip(59 minutes);
        feed.latest();

        aggregator.setData(2, 105);

        skip(61 minutes);
        vm.expectRevert("stale price feed");
        feed.latest();
    }

    function testSetHeartbeat() public {
        vm.startPrank(GOVERNOR);

        feed.setHeartbeat(120 minutes);

        vm.stopPrank();
        aggregator.setData(1, 105);

        skip(119 minutes);
        feed.latest();

        vm.startPrank(GOVERNOR);

        feed.setHeartbeat(30 minutes);

        vm.stopPrank();

        skip(61 minutes);
        vm.expectRevert("stale price feed");
        feed.latest();

        vm.expectRevert();
        feed.setHeartbeat(60 minutes);
    }
}
