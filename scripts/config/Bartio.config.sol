// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library BartioConfig {
    // ---------------- PROTOCOL ADDRESSES ----------------
    address constant V1_FACTORY = 0xBe048017966c2787f548De1Df5834449eC4c4f50;
    address constant FEED_FACTORY = 0xc0dE47Cbb26C2e19B82f9E205b0b0FfcD7947290;
    address constant OVL = 0x97576e088f0d05EF68cac2EEc63d017FE90952a0;

    // ---------------- TOKEN CONFIG ----------------
    address constant GOV = 0x85f66DBe1ed470A091d338CFC7429AA871720283;

    // ---------------- V1 FACTORY CONFIG ----------------
    address constant FEE_RECIPIENT = 0x85f66DBe1ed470A091d338CFC7429AA871720283;
    // Ref: https://docs.chain.link/data-feeds/l2-sequencer-feeds#available-networks
    address constant SEQUENCER_ORACLE = 0xC35093f76fF3D31Af27A893CDcec585F1899eE54;
    uint256 constant GRACE_PERIOD = 1 hours;

    // ---------------- FEED FACTORY CONFIG ----------------
    uint256 constant MICRO_WINDOW = 600;
    uint256 constant MACRO_WINDOW = 3600;
}
