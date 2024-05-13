// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1ChainlinkFeedFactory} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Run with:
// $ source .env
// $ forge script scripts/feeds/chainlink/Deploy.s.sol:DeployFeedFactory --rpc-url $RPC --verify -vvvv --broadcast

contract DeployFeedFactory is Script {
    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->
        
        OverlayV1ChainlinkFeedFactory feedFactory = new OverlayV1ChainlinkFeedFactory(
            ArbSepoliaConfig.OVL,
            ArbSepoliaConfig.MICRO_WINDOW,
            ArbSepoliaConfig.MACRO_WINDOW
        );

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("FeedFactory deployed at:", address(feedFactory));
    }
}
