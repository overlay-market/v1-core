// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

library BalancerV2PoolInfo {
    struct Pool {
        address marketPool;
        address ovlWethPool;
        address ovl;
        address marketBaseToken;
        address marketQuoteToken;
        uint128 marketBaseAmount;
    }
}
