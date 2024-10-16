// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
// $ source .env
// $ forge script scripts/AddFeedFactory.s.sol:AddFeedFactory -vvvv --rpc-url $RPC --broadcast

// NOTE: the periphery contract should be deployed before running this script
contract AddFeedFactory is Script {

    function run() external {
        // NOTE: this should be the private key of the GOVERNOR
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        OverlayV1Factory factory = OverlayV1Factory(0xBe048017966c2787f548De1Df5834449eC4c4f50);
        address feedFactory = 0xc0dE47Cbb26C2e19B82f9E205b0b0FfcD7947290;

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        factory.addFeedFactory(feedFactory);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Added feed factory: ", feedFactory);
        console2.log("To Factory: ", address(factory));
    }
}
