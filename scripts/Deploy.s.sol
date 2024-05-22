// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {MINTER_ROLE, GOVERNOR_ROLE} from "contracts/interfaces/IOverlayV1Token.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Deploy with:
// $ source .env
// $ forge script scripts/Deploy.s.sol:DeployScript --rpc-url $RPC --verify -vvvv --broadcast

contract DeployScript is Script {
    bytes32 constant ADMIN_ROLE = 0x00;

    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");
        address deployer = vm.addr(DEPLOYER_PK);

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        // 1. Deploy token contract
        OverlayV1Token ovl = new OverlayV1Token();

        // 2. Deploy factory contract
        OverlayV1Factory factory = new OverlayV1Factory(
            address(ovl),
            ArbSepoliaConfig.FEE_RECIPIENT,
            ArbSepoliaConfig.SEQUENCER_ORACLE,
            ArbSepoliaConfig.GRACE_PERIOD
        );

        // 3. Grant factory admin role so that it can grant minter + burner roles to markets
        ovl.grantRole(ADMIN_ROLE, address(factory));

        // 4. Grant admin rights to governance
        ovl.grantRole(ADMIN_ROLE, ArbSepoliaConfig.GOV);
        ovl.grantRole(MINTER_ROLE, ArbSepoliaConfig.GOV);
        ovl.grantRole(GOVERNOR_ROLE, ArbSepoliaConfig.GOV);

        // 5. Renounce admin role so only governance has it
        ovl.renounceRole(ADMIN_ROLE, deployer);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Token deployed at:", address(ovl));
        console2.log("Factory deployed at:", address(factory));
    }
}
