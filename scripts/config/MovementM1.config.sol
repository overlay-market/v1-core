// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library MovementM1Config {
    // ---------------- PROTOCOL ADDRESSES ----------------
    address constant V1_FACTORY = 0x3E27fAe625f25291bFda517f74bf41DC40721dA2;
    address constant FEED_FACTORY = 0x0000000000000000000000000000000000000000;
    address constant OVL = 0x7Aee03680CCB1F94d52A76Be010f63BdD9E99Ef9;

    // ---------------- TOKEN CONFIG ----------------
    address constant GOV = 0xc946446711eE82b87cc34611810B0f2DD14c15DD;

    // ---------------- V1 FACTORY CONFIG ----------------
    address constant FEE_RECIPIENT = 0xc946446711eE82b87cc34611810B0f2DD14c15DD;
    // Ref: https://docs.chain.link/data-feeds/l2-sequencer-feeds#available-networks
    address constant SEQUENCER_ORACLE = 0x247Ea97F47832FCCF8B5cDD7BCCc573320aeB328;
    uint256 constant GRACE_PERIOD = 1 hours;

    // ---------------- FEED FACTORY CONFIG ----------------
    uint256 constant MICRO_WINDOW = 600;
    uint256 constant MACRO_WINDOW = 3600;
}
