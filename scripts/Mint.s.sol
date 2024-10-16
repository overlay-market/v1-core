// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
// $ source .env
// $ forge script scripts/Mint.s.sol:MintTokensScript -vvvv --rpc-url $RPC --broadcast 

// NOTE: the periphery contract should be deployed before running this script
contract MintTokensScript is Script {

    function run() external {
        // NOTE: this should be the private key of the GOVERNOR
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        OverlayV1Token token = OverlayV1Token(0xCde46284D32148c4D470fA33BA788710b3d21E89);

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        token.mint(0x85f66DBe1ed470A091d338CFC7429AA871720283, 88_888_888 * 10**18);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Minted tokens:", address(token));
    }
}
