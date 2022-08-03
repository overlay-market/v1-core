// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

library FixedCast {
    uint256 internal constant ONE_256 = 1e18; // 18 decimal places
    uint256 internal constant ONE_16 = 1e4; // 4 decimal places

    /// @dev casts a uint16 to a FixedPoint uint256 with 18 decimals
    function toUint256Fixed(uint16 value) internal pure returns (uint256) {
        uint256 multiplier = ONE_256 / ONE_16;
        return (uint256(value) * multiplier);
    }

    /// @dev casts a FixedPoint uint256 to a uint16 with 4 decimals
    function toUint16Fixed(uint256 value) internal pure returns (uint16) {
        uint256 divisor = ONE_256 / ONE_16;
        uint256 ret256 = value / divisor;
        require(ret256 <= type(uint16).max, "OVLV1: FixedCast out of bounds");
        return uint16(ret256);
    }
}
