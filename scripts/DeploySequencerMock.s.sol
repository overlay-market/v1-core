// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {MockChainlinkSequencerFeed} from "contracts/mocks/SequencerMock.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Deploy with:
// $ source .env
// $ forge script scripts/DeploySequencerMock.s.sol:DeploySequencerMockScript --rpc-url $RPC -vvvv --broadcast --verify 
// --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

contract DeploySequencerMockScript is Script {

    function run() external {
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        // 1. Deploy sequencerMock contract
        MockChainlinkSequencerFeed sequencerMock = new MockChainlinkSequencerFeed();

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("sequencerMock deployed at:", address(sequencerMock));
    }
}
