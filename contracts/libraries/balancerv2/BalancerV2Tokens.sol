// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

library BalancerV2Tokens {
    struct Info {
        address vault;
        bytes32 marketPoolId;
        bytes32 ovlWethPoolId;
    }
}
