// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

library TestUtils {
    // Reference: https://github.com/crytic/properties/blob/main/contracts/util/PropertiesHelper.sol#L240-L259
    function clampBetween(uint256 value, uint256 low, uint256 high)
        internal
        pure
        returns (uint256)
    {
        if (value < low || value > high) {
            return (low + (value % (high - low + 1)));
        }
        return value;
    }

    // Reference: v1-core/lib/forge-std/src/StdAssertions.sol
    function isApproxEqRel(
        uint256 a,
        uint256 b,
        uint256 maxPercentDelta // an 18 decimal fixed point number, where 1e18 == 100%
    ) internal pure returns (bool) {
        if (b == 0) return a == b; // if the right is 0, left must be too.

        return percentDelta(a, b) <= maxPercentDelta;
    }

    function percentDelta(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 absDelta = delta(a, b);

        return absDelta * 1e18 / b;
    }

    function delta(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a - b : b - a;
    }
}
