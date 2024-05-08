// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1ChainlinkFeedFactory} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Run with:
// $ source .env
// $ forge script scripts/feeds/chainlink/Deploy.s.sol:DeployFeedFactory --rpc-url $RPC --verify -vvvv --broadcast

contract DeployFeedFactory is Script {
    // TODO: update values as needed
    address constant OVL = 0x0000000000000000000000000000000000000000;
    uint256 constant MICRO_WINDOW = 600;
    uint256 constant MACRO_WINDOW = 3600;

    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->
        
        OverlayV1ChainlinkFeedFactory feedFactory = new OverlayV1ChainlinkFeedFactory(OVL, MICRO_WINDOW, MACRO_WINDOW);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("FeedFactory deployed at:", address(feedFactory));
    }
}
