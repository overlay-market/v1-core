// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";
import "./FixedPoint.sol";

library Position {
    using FixedPoint for uint256;
    uint256 internal constant TWO = 2e18;

    struct Info {
        uint256 leverage; // discrete initial leverage amount
        bool isLong; // whether long or short
        uint256 entryPrice; // price received at entry
        uint256 oiShares; // shares of open interest
        uint256 debt; // debt
        uint256 cost; // amount of collateral initially locked
    }

    function initialOi(Info memory self) internal view returns (uint256) {
        return _initialOi(self);
    }

    /// @notice Computes the open interest of a position
    function oi(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares
    ) internal view returns (uint256) {
        return _oi(self, totalOi, totalOiShares);
    }

    /// @notice Computes the value of a position
    /// @dev Floors to zero, so won't properly compute if self is underwater
    function value(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) internal view returns (uint256) {
        return _value(self, totalOi, totalOiShares, currentPrice);
    }

    /// @notice Whether position is underwater
    /// @dev is true when position value <= 0
    function isUnderwater(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) internal view returns (bool) {
        return _isUnderwater(self, totalOi, totalOiShares, currentPrice);
    }

    /// @notice Computes the notional of a position
    /// @dev Floors to _self.debt if value <= 0
    function notional(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) internal view returns (uint256) {
        return _notional(self, totalOi, totalOiShares, currentPrice);
    }

    /// @notice Whether a position can be liquidated
    /// @dev is true when value < maintenance margin
    function isLiquidatable(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 marginMaintenance
    ) internal view returns (bool) {
        return _isLiquidatable(self, totalOi, totalOiShares, currentPrice, marginMaintenance);
    }

    /// @notice Computes the liquidation price of a position
    /// @dev price when value < maintenance margin
    function liquidationPrice(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 marginMaintenance
    ) internal view returns (uint256) {
        return _liquidationPrice(self, totalOi, totalOiShares, marginMaintenance);
    }

    function _initialOi(Info memory self) private pure returns (uint256) {
        return self.cost + self.debt;
    }

    /// @dev returns zero when oiShares = totalOi = totalOiShares = 0 to avoid
    /// div by zero errors
    function _oi(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares
    ) private pure returns (uint256) {
        if (self.oiShares == 0 || totalOi == 0) return 0;
        return self.oiShares.mulDown(totalOi).divUp(totalOiShares);
    }

    /// @dev Floors to zero, so won't properly compute if self is underwater
    function _value(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) private pure returns (uint256 val_) {
        uint256 currentOi = _oi(self, totalOi, totalOiShares);
        if (self.isLong) {
            // oi * priceFrame - debt
            uint256 priceFrame = currentPrice.divDown(self.entryPrice);
            val_ = currentOi.mulDown(priceFrame);
            val_ -= Math.min(val_, self.debt); // floor to 0
        } else {
            // oi * (2 - priceFrame) - debt
            uint256 priceFrame = currentPrice.divUp(self.entryPrice);
            val_ = currentOi.mulDown(TWO);
            val_ -= Math.min(val_, self.debt + currentOi.mulDown(priceFrame)); // floor to 0
        }
    }

    /// @dev is true when position value < 0
    function _isUnderwater(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) private pure returns (bool isUnder_) {
        uint256 currentOi = _oi(self, totalOi, totalOiShares);
        bool long = self.isLong;
        if (long) {
            uint256 priceFrame = currentPrice.divDown(self.entryPrice);
            isUnder_ = currentOi.mulDown(priceFrame) < self.debt;
        } else {
            uint256 priceFrame = currentPrice.divUp(self.entryPrice);
            isUnder_ = currentOi.mulDown(priceFrame) + self.debt > currentOi.mulDown(TWO);
        }
    }

    /// @dev Floors to zero, so won't properly compute if _self is underwater
    function _notional(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) private pure returns (uint256 notional_) {
        uint256 currentOi = _oi(self, totalOi, totalOiShares);
        if (self.isLong) {
            // oi * priceFrame
            uint256 priceFrame = currentPrice.divDown(self.entryPrice);
            notional_ = currentOi.mulDown(priceFrame);
        } else {
            // oi * (2 - priceFrame)
            uint256 priceFrame = currentPrice.divUp(self.entryPrice);
            notional_ = currentOi.mulDown(TWO);
            notional_ -= Math.min(notional_, currentOi.mulDown(priceFrame)); // floor to 0
        }
    }

    /// @dev is true when open margin < maintenance margin
    function _isLiquidatable(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 marginMaintenance
    ) private pure returns (bool can_) {
        uint256 val = _value(self, totalOi, totalOiShares, currentPrice);
        uint256 maintenanceMargin = _initialOi(self).mulUp(marginMaintenance);
        can_ = val < maintenanceMargin;
    }

    function _liquidationPrice(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 marginMaintenance
    ) private pure returns (uint256 liqPrice_) {
        uint256 posOi = _oi(self, totalOi, totalOiShares);
        uint256 posInitialOi = _initialOi(self);

        // TODO: decide what to return when posOi = 0 to avoid
        // div by zero error

        uint256 oiFrame = posInitialOi.mulUp(marginMaintenance).add(self.debt).divDown(posOi);

        if (self.isLong) {
            liqPrice_ = self.entryPrice.mulUp(oiFrame);
        } else {
            liqPrice_ = self.entryPrice.mulUp(TWO.sub(oiFrame));
        }
    }
}
