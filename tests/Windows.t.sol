// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {OverlayV1Deployer} from "contracts/OverlayV1Deployer.sol";
import {Position} from "contracts/libraries/Position.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";
import {OverlayV1ChainlinkFeed} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import {OverlayV1ChainlinkFeedFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";
import {Oracle} from "contracts/libraries/Oracle.sol";

contract WindowsTest is Test {
    AggregatorMock aggregator;
    OverlayV1ChainlinkFeed feed;
    OverlayV1ChainlinkFeedFactory feedFactory;
    OverlayV1Token ov;
    bytes32 constant GOVERNOR_ROLE = keccak256("GOVERNOR");
    address immutable GOVERNOR = makeAddr("governor");

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC"), 169_490_320);
        ov = new OverlayV1Token();
        aggregator = new AggregatorMock();
        feedFactory = new OverlayV1ChainlinkFeedFactory(address(ov), 1, 1);
        feed = OverlayV1ChainlinkFeed(feedFactory.deployFeed(address(aggregator), 60 minutes));
        ov.grantRole(GOVERNOR_ROLE, GOVERNOR);
    }

    function testMinMicroMacro() public {
        aggregator.setData(1, 9136261083505);

        skip(30 minutes);
        Oracle.Data memory data = feed.latest();

        console2.log("data.priceOverMicroWindow", data.priceOverMicroWindow);
        console2.log("data.priceOverMacroWindow", data.priceOverMacroWindow);

        aggregator.setData(2, 9142360788087);

        skip(30 minutes);
        feed.latest();

        aggregator.setData(3, 9152360788087);
    }
}
