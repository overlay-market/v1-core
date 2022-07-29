// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/SignedMath.sol";

import "./FixedPoint.sol";

library Tick {
    using FixedPoint for uint256;
    using SignedMath for int256;

    uint256 internal constant ONE = 1e18;
    uint256 internal constant PRICE_BASE = 1.0001e18;
    int256 internal constant MAX_TICK_256 = 120e22;
    int256 internal constant MIN_TICK_256 = -41e22;

    /// @notice Computes the tick associated with the given price
    /// @notice where price = 1.0001 ** tick
    /// @dev FixedPoint lib constraints on min/max natural exponent of
    /// @dev -41e18, 130e18 respectively, means min/max tick will be
    /// @dev -41e18/ln(1.0001), 130e18/ln(1.0001), respectively (w some buffer)
    function priceToTick(uint256 price) internal pure returns (int24) {
        int256 tick256 = price.logDown(PRICE_BASE);
        require(tick256 >= MIN_TICK_256 && tick256 <= MAX_TICK_256, "OVLV1: tick out of bounds");

        // tick256 is FixedPoint format with 18 decimals. Divide by ONE
        // then truncate to int24
        return int24(tick256 / int256(ONE));
    }

    /// @notice Computes the price associated with the given tick
    /// @notice where price = 1.0001 ** tick
    /// @dev FixedPoint lib constraints on min/max natural exponent of
    /// @dev -41e18, 130e18 respectively, means min/max tick will be
    /// @dev -41e18/ln(1.0001), 130e18/ln(1.0001), respectively (w some buffer)
    function tickToPrice(int24 tick) internal pure returns (uint256) {
        // tick needs to be converted to Fixed point format with 18 decimals
        // to use FixedPoint powUp
        int256 tick256 = int256(tick) * int256(ONE);
        require(tick256 >= MIN_TICK_256 && tick256 <= MAX_TICK_256, "OVLV1: tick out of bounds");

        uint256 pow = uint256(tick256.abs());
        return (tick256 >= 0 ? PRICE_BASE.powDown(pow) : ONE.divDown(PRICE_BASE.powUp(pow)));
    }
}
