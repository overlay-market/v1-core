// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library ArbMainnetConfig {
    // ---------------- PROTOCOL ADDRESSES ----------------
    address constant V1_FACTORY = 0x5161F15B3Ec704c03cFfF18ca44fa7C68f1788e8;
    address constant FEED_FACTORY = 0x0000000000000000000000000000000000000000;
    address constant OVL = 0x92E6eBF555F834F7214e788e576640e4c13C2B97;

    // ---------------- TOKEN CONFIG ----------------
    address constant GOV = 0x5985FD48b48fdde2C5c1BC0b4f591c83D961184B;

    // ---------------- V1 FACTORY CONFIG ----------------
    address constant FEE_RECIPIENT = 0x5985FD48b48fdde2C5c1BC0b4f591c83D961184B;
    // Ref: https://docs.chain.link/data-feeds/l2-sequencer-feeds#available-networks
    address constant SEQUENCER_ORACLE = 0xFdB631F5EE196F0ed6FAa767959853A9F217697D;
    uint256 constant GRACE_PERIOD = 1 hours; // same as aave's https://arbiscan.io/address/0x7A9ff54A6eE4a21223036890bB8c4ea2D62c686b#readContract#F2

    // ---------------- FEED FACTORY CONFIG ----------------
    uint256 constant MICRO_WINDOW = 600;
    uint256 constant MACRO_WINDOW = 3600;
}
