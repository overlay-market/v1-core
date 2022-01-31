// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";
import "./FixedPoint.sol";

library Position {
    using FixedPoint for uint256;
    uint256 internal constant TWO = 2e18;

    struct Info {
        uint120 oi; // initial open interest
        uint120 debt; // debt
        bool isLong; // whether long or short
        bool liquidated; // whether has been liquidated
        uint256 entryPrice; // price received at entry
    }

    /*///////////////////////////////////////////////////////////////
                        POSITIONS MAPPING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Retrieves a position from positions mapping
    function get(
        mapping(bytes32 => Info) storage self,
        address owner,
        uint256 id
    ) internal view returns (Info storage position_) {
        position_ = self[keccak256(abi.encodePacked(owner, id))];
    }

    /// @notice Stores a position in positions mapping
    function set(
        mapping(bytes32 => Info) storage self,
        address owner,
        uint256 id,
        Info memory position
    ) internal {
        self[keccak256(abi.encodePacked(owner, id))] = position;
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the position's initial open interest
    function _oiInitial(Info memory self) private pure returns (uint256) {
        return uint256(self.oi);
    }

    /// @notice Computes the position's debt
    function _debt(Info memory self) private pure returns (uint256) {
        return uint256(self.debt);
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    // TODO: functions to compute more properties:
    // TODO: e.g. collateralInitial, leverageInitial, cost, ....

    /// @notice Computes the open interest of a position
    function oiCurrent(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares
    ) internal view returns (uint256) {
        return _oiCurrent(self, totalOi, totalOiShares);
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

    /// @dev returns zero when oiShares = totalOi = totalOiShares = 0 to avoid
    /// div by zero errors
    function _oiCurrent(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares
    ) private pure returns (uint256) {
        uint256 initialOi = _oiInitial(self);
        if (initialOi == 0 || totalOi == 0) return 0;
        return initialOi.mulDown(totalOi).divUp(totalOiShares);
    }

    /// @dev Floors to zero, so won't properly compute if self is underwater
    function _value(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) private pure returns (uint256 val_) {
        uint256 currentOi = _oiCurrent(self, totalOi, totalOiShares);
        uint256 debt = _debt(self);
        uint256 entryPrice = self.entryPrice;
        if (self.isLong) {
            // oi * priceFrame - debt
            uint256 priceFrame = currentPrice.divDown(entryPrice);
            val_ = currentOi.mulDown(priceFrame);
            val_ -= Math.min(val_, debt); // floor to 0
        } else {
            // oi * (2 - priceFrame) - debt
            uint256 priceFrame = currentPrice.divUp(entryPrice);
            val_ = currentOi.mulDown(TWO);
            val_ -= Math.min(val_, debt + currentOi.mulDown(priceFrame)); // floor to 0
        }
    }

    /// @dev is true when position value < 0
    function _isUnderwater(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) private pure returns (bool isUnder_) {
        uint256 currentOi = _oiCurrent(self, totalOi, totalOiShares);
        uint256 debt = _debt(self);
        uint256 entryPrice = self.entryPrice;
        if (self.isLong) {
            uint256 priceFrame = currentPrice.divDown(entryPrice);
            isUnder_ = currentOi.mulDown(priceFrame) < debt;
        } else {
            uint256 priceFrame = currentPrice.divUp(entryPrice);
            isUnder_ = currentOi.mulDown(priceFrame) + debt > currentOi.mulDown(TWO);
        }
    }

    /// @dev Floors to zero, so won't properly compute if _self is underwater
    function _notional(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) private pure returns (uint256 notional_) {
        uint256 currentOi = _oiCurrent(self, totalOi, totalOiShares);
        uint256 entryPrice = self.entryPrice;
        if (self.isLong) {
            // oi * priceFrame
            uint256 priceFrame = currentPrice.divDown(entryPrice);
            notional_ = currentOi.mulDown(priceFrame);
        } else {
            // oi * (2 - priceFrame)
            uint256 priceFrame = currentPrice.divUp(entryPrice);
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
        uint256 oiInitial = _oiInitial(self);

        if (self.liquidated) {
            // already been liquidated
            return false;
        }

        uint256 val = _value(self, totalOi, totalOiShares, currentPrice);
        uint256 maintenanceMargin = oiInitial.mulUp(marginMaintenance);
        can_ = val < maintenanceMargin;
    }

    function _liquidationPrice(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 marginMaintenance
    ) private pure returns (uint256 liqPrice_) {
        uint256 posOiCurrent = _oiCurrent(self, totalOi, totalOiShares);
        uint256 posOiInitial = _oiInitial(self);
        uint256 debt = _debt(self);

        // TODO: test
        if (self.liquidated) {
            // return 0 if already liquidated
            return 0;
        }

        uint256 oiFrame = posOiInitial.mulUp(marginMaintenance).add(debt).divDown(posOiCurrent);

        if (self.isLong) {
            liqPrice_ = self.entryPrice.mulUp(oiFrame);
        } else {
            liqPrice_ = self.entryPrice.mulUp(TWO.sub(oiFrame));
        }
    }
}
