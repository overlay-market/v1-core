// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "../libraries/Tick.sol";

contract TickMock {
    function priceToTick(uint256 price) external pure returns (int24) {
        return Tick.priceToTick(price);
    }

    function tickToPrice(int24 tick) external pure returns (uint256) {
        return Tick.tickToPrice(tick);
    }
}
