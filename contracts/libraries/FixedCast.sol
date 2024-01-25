// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

library FixedCast {
    uint256 internal constant PRECISION_CHANGER = 1e14;

    /// @dev casts a uint16 to a FixedPoint uint256 with 18 decimals
    /// @dev increases precision by 14 decimals
    function toUint256Fixed(uint16 value) internal pure returns (uint256) {
        return (uint256(value) * PRECISION_CHANGER);
    }

    /// @dev casts a FixedPoint uint256 to a uint16 with 4 decimals
    /// @dev decreases precision by 14 decimals
    function toUint16Fixed(uint256 value) internal pure returns (uint16) {
        uint256 ret256 = value / PRECISION_CHANGER;
        require(ret256 <= type(uint16).max, "OVV1: FixedCast out of bounds");
        return uint16(ret256);
    }
}
