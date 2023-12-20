// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Script} from "forge-std/Script.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";

bytes32 constant MINTER_ROLE = keccak256("MINTER");
bytes32 constant GOVERNOR_ROLE = keccak256("GOVERNOR");
bytes32 constant EMERGENCY_ROLE = keccak256("EMERGENCY");

contract Deploy is Script {
    OverlayV1Token public ovl;

    function _deploy() internal {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address GOVERNOR = vm.envAddress("GOVERNOR");
        address EMERGENCY_MULTISIG = vm.envAddress("EMERGENCY_MULTISIG");
        address FEE_RECIPIENT = vm.envAddress("FEE_RECIPIENT");

        vm.startBroadcast(deployerPrivateKey);
        ovl = new OverlayV1Token();
        new OverlayV1Factory(address(ovl), FEE_RECIPIENT);

        ovl.grantRole(0x00, GOVERNOR);
        ovl.grantRole(MINTER_ROLE, GOVERNOR);
        ovl.grantRole(GOVERNOR_ROLE, GOVERNOR);
        ovl.grantRole(EMERGENCY_ROLE, EMERGENCY_MULTISIG);

        ovl.renounceRole(0x00, address(uint160(deployerPrivateKey)));

        vm.stopBroadcast();
    }
}

/* If it doesn't verify automatically, run:
forge verify-contract \
    --chain-id 421614 \
    --num-of-optimizations 200 \
    --watch \
    --etherscan-api-key <api> \
    --compiler-version v0.8.10 \
    <contractAddress> \
    contracts/<contractFile>.sol:<contractName> \

*/
