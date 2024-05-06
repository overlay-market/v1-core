// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Token} from "../contracts/OverlayV1Token.sol";
import {MINTER_ROLE, GOVERNOR_ROLE} from "../contracts/interfaces/IOverlayV1Token.sol";
import {OverlayV1Factory} from "../contracts/OverlayV1Factory.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Deploy with:
// $ source .env
// $ forge script script/Deploy.s.sol:DeployScript --rpc-url $RPC --verify -vvvv --broadcast

contract DeployScript is Script {
    bytes32 constant ADMIN_ROLE = 0x00;

    address constant GOV = 0x95f972fc4D17a0D343Cd5eaD8d6DCBef5606CA66;
    address constant FEE_RECIPIENT = 0xDFafdfF09C1d63257892A8d2F56483588B99315A;

    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");
        address deployer = vm.addr(DEPLOYER_PK);

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->
        
        // 1. Deploy token contract
        OverlayV1Token ovl = new OverlayV1Token();

        // 2. Deploy factory contract
        // Ref: https://docs.chain.link/data-feeds/l2-sequencer-feeds#available-networks
        address sequencerOracle = 0xFdB631F5EE196F0ed6FAa767959853A9F217697D;
        uint256 gracePeriod = 1 hours;
        OverlayV1Factory factory = new OverlayV1Factory(
            address(ovl),
            FEE_RECIPIENT,
            sequencerOracle,
            gracePeriod
        );

        // 3. Grant factory admin role so that it can grant minter + burner roles to markets
        ovl.grantRole(ADMIN_ROLE, address(factory));

        // 4. Grant admin rights to governance
        ovl.grantRole(ADMIN_ROLE, GOV);
        ovl.grantRole(MINTER_ROLE, GOV);
        ovl.grantRole(GOVERNOR_ROLE, GOV);

        // 5. Renounce admin role so only governance has it
        ovl.renounceRole(ADMIN_ROLE, deployer);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();
    }
}
