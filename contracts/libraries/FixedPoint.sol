// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// COPIED AND MODIFIED FROM:
// @balancer-v2-monorepo/pkg/solidity-utils/contracts/math/FixedPoint.sol
// XXX for changes

// XXX: 0.8.10; removed requires for overflow checks
pragma solidity 0.8.10;

import "./LogExpMath.sol";

/* solhint-disable private-vars-leading-underscore */

library FixedPoint {
    uint256 internal constant ONE = 1e18; // 18 decimal places
    uint256 internal constant TWO = 2 * ONE;
    uint256 internal constant FOUR = 4 * ONE;
    uint256 internal constant MAX_POW_RELATIVE_ERROR = 10000; // 10^(-14)

    // Minimum base for the power function when the exponent is 'free' (larger than ONE).
    uint256 internal constant MIN_POW_BASE_FREE_EXPONENT = 0.7e18;

    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        // Fixed Point addition is the same as regular checked addition
        uint256 c = a + b;
        return c;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        // Fixed Point addition is the same as regular checked addition
        uint256 c = a - b;
        return c;
    }

    /// @notice a - b but floors to zero if a <= b
    /// XXX: subFloor implementation
    function subFloor(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a > b ? a - b : 0;
        return c;
    }

    function mulDown(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 product = a * b;
        return product / ONE;
    }

    function mulUp(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 product = a * b;
        if (product == 0) {
            return 0;
        } else {
            // The traditional divUp formula is:
            // divUp(x, y) := (x + y - 1) / y
            // To avoid intermediate overflow in the addition, we distribute the division and get:
            // divUp(x, y) := (x - 1) / y + 1
            // Note that this requires x != 0, which we already tested for.
            return ((product - 1) / ONE) + 1;
        }
    }

    function divDown(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) {
            return 0;
        } else {
            uint256 aInflated = a * ONE;
            return aInflated / b;
        }
    }

    function divUp(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) {
            return 0;
        } else {
            uint256 aInflated = a * ONE;
            // The traditional divUp formula is:
            // divUp(x, y) := (x + y - 1) / y
            // To avoid intermediate overflow in the addition, we distribute the division and get:
            // divUp(x, y) := (x - 1) / y + 1
            // Note that this requires x != 0, which we already tested for.
            return ((aInflated - 1) / b) + 1;
        }
    }

    /**
     * @dev Returns x^y, assuming both are fixed point numbers, rounding down.
     * The result is guaranteed to not be above the true value (that is,
     * the error function expected - actual is always positive).
     */
    function powDown(uint256 x, uint256 y) internal pure returns (uint256) {
        // Optimize for when y equals 1.0, 2.0 or 4.0, as those are very simple
        // to implement and occur often in 50/50 and 80/20 Weighted Pools
        // XXX: checks for y == 0, x == ONE, x == 0
        if (0 == y || x == ONE) {
            return ONE;
        } else if (x == 0) {
            return 0;
        } else if (y == ONE) {
            return x;
        } else if (y == TWO) {
            return mulDown(x, x);
        } else if (y == FOUR) {
            uint256 square = mulDown(x, x);
            return mulDown(square, square);
        } else {
            uint256 raw = LogExpMath.pow(x, y);
            uint256 maxError = add(mulUp(raw, MAX_POW_RELATIVE_ERROR), 1);

            if (raw < maxError) {
                return 0;
            } else {
                return sub(raw, maxError);
            }
        }
    }

    /**
     * @dev Returns x^y, assuming both are fixed point numbers, rounding up.
     * The result is guaranteed to not be below the true value (that is,
     * the error function expected - actual is always negative).
     */
    function powUp(uint256 x, uint256 y) internal pure returns (uint256) {
        // Optimize for when y equals 1.0, 2.0 or 4.0, as those are very simple
        // to implement and occur often in 50/50 and 80/20 Weighted Pools
        // XXX: checks for y == 0, x == ONE, x == 0
        if (0 == y || x == ONE) {
            return ONE;
        } else if (x == 0) {
            return 0;
        } else if (y == ONE) {
            return x;
        } else if (y == TWO) {
            return mulUp(x, x);
        } else if (y == FOUR) {
            uint256 square = mulUp(x, x);
            return mulUp(square, square);
        } else {
            uint256 raw = LogExpMath.pow(x, y);
            uint256 maxError = add(mulUp(raw, MAX_POW_RELATIVE_ERROR), 1);

            return add(raw, maxError);
        }
    }

    /**
     * @dev Returns e^x, assuming x is a fixed point number, rounding down.
     * The result is guaranteed to not be above the true value (that is,
     * the error function expected - actual is always positive).
     * XXX: expDown implementation
     */
    function expDown(uint256 x) internal pure returns (uint256) {
        if (x == 0) {
            return ONE;
        }
        require(x < 2**255, "FixedPoint: x out of bounds");

        int256 x_int256 = int256(x);
        uint256 raw = uint256(LogExpMath.exp(x_int256));
        uint256 maxError = add(mulUp(raw, MAX_POW_RELATIVE_ERROR), 1);

        if (raw < maxError) {
            return 0;
        } else {
            return sub(raw, maxError);
        }
    }

    /**
     * @dev Returns e^x, assuming x is a fixed point number, rounding up.
     * The result is guaranteed to not be below the true value (that is,
     * the error function expected - actual is always negative).
     * XXX: expUp implementation
     */
    function expUp(uint256 x) internal pure returns (uint256) {
        if (x == 0) {
            return ONE;
        }
        require(x < 2**255, "FixedPoint: x out of bounds");

        int256 x_int256 = int256(x);
        uint256 raw = uint256(LogExpMath.exp(x_int256));
        uint256 maxError = add(mulUp(raw, MAX_POW_RELATIVE_ERROR), 1);

        return add(raw, maxError);
    }

    /**
     * @dev Returns log_b(a), assuming a, b are fixed point numbers, rounding down.
     * The result is guaranteed to not be above the true value (that is,
     * the error function expected - actual is always positive).
     * XXX: logDown implementation
     */
    function logDown(uint256 a, uint256 b) internal pure returns (int256) {
        require(a > 0 && a < 2**255, "FixedPoint: a out of bounds");
        require(b > 0 && b < 2**255, "FixedPoint: b out of bounds");

        int256 arg = int256(a);
        int256 base = int256(b);
        int256 raw = LogExpMath.log(arg, base);

        // NOTE: see @openzeppelin/contracts/utils/math/SignedMath.sol#L37
        uint256 rawAbs;
        unchecked {
            rawAbs = uint256(raw >= 0 ? raw : -raw);
        }
        uint256 maxError = add(mulUp(rawAbs, MAX_POW_RELATIVE_ERROR), 1);
        return raw - int256(maxError);
    }

    /**
     * @dev Returns log_b(a), assuming a, b are fixed point numbers, rounding up.
     * The result is guaranteed to not be below the true value (that is,
     * the error function expected - actual is always negative).
     * XXX: logUp implementation
     */
    function logUp(uint256 a, uint256 b) internal pure returns (int256) {
        require(a > 0 && a < 2**255, "FixedPoint: a out of bounds");
        require(b > 0 && b < 2**255, "FixedPoint: b out of bounds");

        int256 arg = int256(a);
        int256 base = int256(b);
        int256 raw = LogExpMath.log(arg, base);

        // NOTE: see @openzeppelin/contracts/utils/math/SignedMath.sol#L37
        uint256 rawAbs;
        unchecked {
            rawAbs = uint256(raw >= 0 ? raw : -raw);
        }
        uint256 maxError = add(mulUp(rawAbs, MAX_POW_RELATIVE_ERROR), 1);
        return raw + int256(maxError);
    }

    /**
     * @dev Returns the complement of a value (1 - x), capped to 0 if x is larger than 1.
     *
     * Useful when computing the complement for values with some level of relative error,
     * as it strips this error and prevents intermediate negative values.
     */
    function complement(uint256 x) internal pure returns (uint256) {
        return (x < ONE) ? (ONE - x) : 0;
    }
}
