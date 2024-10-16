// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1ChainlinkFeedFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";
import {MovementM1Config} from "scripts/config/MovementM1.config.sol";
import {BartioConfig} from "scripts/config/Bartio.config.sol";
import {InternalMovementM1Config} from "scripts/config/InternalMovementM1.config.sol";
import {ImolaMovementConfig} from "scripts/config/ImolaMovement.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
// $ source .env
// $ forge script scripts/feeds/chainlink/Deploy.s.sol:DeployFeedFactory --rpc-url $RPC -vvvv --broadcast --verify

contract DeployFeedFactory is Script {
    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        OverlayV1ChainlinkFeedFactory feedFactory = new OverlayV1ChainlinkFeedFactory(
            BartioConfig.OVL, BartioConfig.MICRO_WINDOW, BartioConfig.MACRO_WINDOW
        );

        // <!-- END DEPLOYMENT -->

        console2.log("OVL address", feedFactory.OV());

        vm.stopBroadcast();

        console2.log("FeedFactory deployed at:", address(feedFactory));
    }
}
