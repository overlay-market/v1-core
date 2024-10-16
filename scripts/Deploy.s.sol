// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {MINTER_ROLE, GOVERNOR_ROLE, GUARDIAN_ROLE, PAUSER_ROLE, RISK_MANAGER_ROLE} from "contracts/interfaces/IOverlayV1Token.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";
import {MovementM1Config} from "scripts/config/MovementM1.config.sol";
import {BartioConfig} from "scripts/config/Bartio.config.sol";
import {InternalMovementM1Config} from "scripts/config/InternalMovementM1.config.sol";
import {ImolaMovementConfig} from "scripts/config/ImolaMovement.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Deploy with:
// $ source .env
// $ forge script scripts/Deploy.s.sol:DeployScript --rpc-url $RPC -vvvv --broadcast --verify
// $ forge script scripts/Deploy.s.sol:DeployScript --rpc-url $RPC -vvvv --broadcast --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan'

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
            BartioConfig.FEE_RECIPIENT,
            BartioConfig.SEQUENCER_ORACLE,
            BartioConfig.GRACE_PERIOD
        );

        // 3. Grant factory admin role so that it can grant minter + burner roles to markets
        ovl.grantRole(ADMIN_ROLE, address(factory));

        // 4. Grant admin rights to governance
        if (deployer != BartioConfig.GOV) revert("something went wrong");
        if (deployer != BartioConfig.GOV) ovl.grantRole(ADMIN_ROLE, BartioConfig.GOV);
        ovl.grantRole(MINTER_ROLE, BartioConfig.GOV);
        ovl.grantRole(GOVERNOR_ROLE, BartioConfig.GOV);
        ovl.grantRole(GUARDIAN_ROLE, BartioConfig.GOV);
        ovl.grantRole(PAUSER_ROLE, BartioConfig.GOV);
        ovl.grantRole(RISK_MANAGER_ROLE, BartioConfig.GOV);

        // 5. Renounce admin role so only governance has it
        if (deployer != BartioConfig.GOV) ovl.renounceRole(ADMIN_ROLE, deployer);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Token symbol:", ovl.symbol());
        console2.log("Token deployed at:", address(ovl));
        console2.log("Factory deployed at:", address(factory));
    }
}
