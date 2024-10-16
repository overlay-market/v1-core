// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library ImolaMovementConfig {
    // ---------------- PROTOCOL ADDRESSES ----------------
    address constant V1_FACTORY = 0xb136c8f0EA9D1c3F676f91FeacEA8BF967fDA7d0;
    address constant FEED_FACTORY = 0xef0cba735406Bc5F698656A8219Ff0d09EaB5d31;
    address constant OVL = 0xCde46284D32148c4D470fA33BA788710b3d21E89;

    // ---------------- TOKEN CONFIG ----------------
    address constant GOV = 0x85f66DBe1ed470A091d338CFC7429AA871720283;

    // ---------------- V1 FACTORY CONFIG ----------------
    address constant FEE_RECIPIENT = 0x85f66DBe1ed470A091d338CFC7429AA871720283;
    // Ref: https://docs.chain.link/data-feeds/l2-sequencer-feeds#available-networks
    address constant SEQUENCER_ORACLE = 0xB9A378CE9CDf3CD5c3ce79869008135a21aDc3A8;
    uint256 constant GRACE_PERIOD = 1 hours;

    // ---------------- FEED FACTORY CONFIG ----------------
    uint256 constant MICRO_WINDOW = 600;
    uint256 constant MACRO_WINDOW = 3600;
}
