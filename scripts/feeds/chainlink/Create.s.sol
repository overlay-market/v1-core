// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1ChainlinkFeedFactory} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Run with:
// $ source .env
// $ forge script scripts/feeds/chainlink/Create.s.sol:CreateFeed --rpc-url $RPC --verify -vvvv --broadcast

contract CreateFeed is Script {
    // TODO: update values as needed
    address constant FEED_FACTORY = 0x0000000000000000000000000000000000000000;
    address constant AGGREGATOR = 0x0000000000000000000000000000000000000000;
    uint256 constant HEARTBEAT = 120 minutes;

    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        vm.startBroadcast(DEPLOYER_PK);

        OverlayV1ChainlinkFeedFactory feedFactory = OverlayV1ChainlinkFeedFactory(FEED_FACTORY);

        // <!---- START DEPLOYMENT ---->

        address feed = feedFactory.deployFeed(AGGREGATOR, HEARTBEAT);        

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Feed deployed at:", feed);
    }
}
