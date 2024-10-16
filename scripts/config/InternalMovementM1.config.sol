// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library InternalMovementM1Config {
    // ---------------- PROTOCOL ADDRESSES ----------------
    address constant V1_FACTORY = 0x1F34c87ded863Fe3A3Cd76FAc8adA9608137C8c3;
    address constant FEED_FACTORY = 0x10575a9C8F36F9F42D7DB71Ef179eD9BEf8Df238;
    address constant OVL = 0x055616C6E3965F90A82120d675C17409B64DB20E;

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
