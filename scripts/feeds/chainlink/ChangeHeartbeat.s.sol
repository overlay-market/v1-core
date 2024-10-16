// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1ChainlinkFeed} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";
import {InternalMovementM1Config} from "scripts/config/InternalMovementM1.config.sol";
import {BartioConfig} from "scripts/config/Bartio.config.sol";
import {ImolaMovementConfig} from "scripts/config/ImolaMovement.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
// $ source .env
// $ forge script scripts/feeds/chainlink/ChangeHeartbeat.s.sol:ChangeHeartbeat --rpc-url $RPC -vvvv --broadcast

contract ChangeHeartbeat is Script {
    // TODO: update values as needed
    address constant feed = 0x43429AECD659324e136429FdF23Ba11cE489FA9e;
    uint256 constant newHeartbeat = 2 days;

    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        OverlayV1ChainlinkFeed(feed).setHeartbeat(newHeartbeat);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("New heartbeat set to", OverlayV1ChainlinkFeed(feed).heartbeat());
    }
}
