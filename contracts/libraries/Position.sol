// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";
import "./FixedPoint.sol";

library Position {
    using FixedPoint for uint256;
    uint256 internal constant ONE = 1e18;

    struct Info {
        uint120 oiShares; // initial open interest
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

    /// @notice Computes the position's initial open interest cast to uint256
    function _oiShares(Info memory self) private pure returns (uint256) {
        return uint256(self.oiShares);
    }

    /// @notice Computes the position's debt cast to uint256
    function _debt(Info memory self) private pure returns (uint256) {
        return uint256(self.debt);
    }

    /// @notice Whether the position exists
    /// @dev Is false if position has been liquidated or has zero oi
    function exists(Info memory self) internal pure returns (bool exists_) {
        return (!self.liquidated && self.oiShares > 0);
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    // TODO: test
    function oiSharesCurrent(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _oiShares(self).mulDown(fraction);
    }

    // TODO: test
    function debtCurrent(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _debt(self).mulDown(fraction);
    }

    // TODO: test
    function oiInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _oiShares(self).mulDown(fraction);
    }

    /// @notice Computes the open interest of a position
    /// @dev returns zero when oiShares = totalOi = totalOiShares = 0 to avoid
    /// @dev div by zero errors
    // TODO: test w fraction
    function oiCurrent(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares
    ) internal pure returns (uint256) {
        uint256 posOiShares = _oiShares(self);
        if (posOiShares == 0 || totalOi == 0) return 0;
        return posOiShares.mulDown(totalOi).divUp(totalOiShares);
    }

    /// @notice Computes the position's cost cast to uint256
    /// WARNING: be careful modifying oi and debt on unwind
    function cost(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return uint256(self.oiShares - self.debt).mulDown(fraction);
    }

    /// @notice Computes the value of a position
    /// @dev Floors to zero, so won't properly compute if self is underwater
    // TODO: test w fraction
    function value(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) internal pure returns (uint256 val_) {
        uint256 posOi = oiCurrent(self, fraction, totalOi, totalOiShares);
        uint256 posDebt = debtCurrent(self, fraction);
        uint256 entryPrice = self.entryPrice;
        if (self.isLong) {
            // oi * priceFrame - debt
            uint256 priceFrame = currentPrice.divDown(entryPrice);
            val_ = posOi.mulDown(priceFrame);
            val_ -= Math.min(val_, posDebt); // floor to 0
        } else {
            // oi * (2 - priceFrame) - debt
            uint256 priceFrame = currentPrice.divUp(entryPrice);
            val_ = posOi.mulDown(2 * ONE);
            val_ -= Math.min(val_, posDebt + posOi.mulDown(priceFrame)); // floor to 0
        }
    }

    /// @notice Computes the notional of a position
    /// @dev Floors to debt if value <= 0
    // TODO: test w fraction
    function notional(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) internal pure returns (uint256 notional_) {
        uint256 posOi = oiCurrent(self, fraction, totalOi, totalOiShares);
        uint256 entryPrice = self.entryPrice;
        if (self.isLong) {
            // oi * priceFrame
            uint256 priceFrame = currentPrice.divDown(entryPrice);
            notional_ = posOi.mulDown(priceFrame);
        } else {
            // oi * (2 - priceFrame)
            uint256 priceFrame = currentPrice.divUp(entryPrice);
            notional_ = posOi.mulDown(2 * ONE);
            notional_ -= Math.min(notional_, posOi.mulDown(priceFrame)); // floor to 0
        }
    }

    // TODO: test
    function tradingFee(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 tradingFeeRate
    ) internal pure returns (uint256 tradingFee_) {
        uint256 posNotional = notional(self, fraction, totalOi, totalOiShares, currentPrice);
        tradingFee_ = posNotional.mulUp(tradingFeeRate);
    }

    // TODO: pnl(), tradingFee()

    /// @notice Whether position is underwater
    /// @dev is true when position value <= 0
    function isUnderwater(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) internal pure returns (bool isUnder_) {
        uint256 posOi = oiCurrent(self, ONE, totalOi, totalOiShares);
        uint256 posDebt = debtCurrent(self, ONE);
        uint256 entryPrice = self.entryPrice;
        if (self.isLong) {
            uint256 priceFrame = currentPrice.divDown(entryPrice);
            isUnder_ = posOi.mulDown(priceFrame) < posDebt;
        } else {
            uint256 priceFrame = currentPrice.divUp(entryPrice);
            isUnder_ = posOi.mulDown(priceFrame) + posDebt > posOi.mulDown(2 * ONE);
        }
    }

    /// @notice Whether a position can be liquidated
    /// @dev is true when value < maintenance margin
    function isLiquidatable(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 marginMaintenance
    ) internal pure returns (bool can_) {
        uint256 posOiInitial = oiInitial(self, ONE);

        if (self.liquidated || posOiInitial == 0) {
            // already been liquidated
            return false;
        }

        uint256 val = value(self, ONE, totalOi, totalOiShares, currentPrice);
        uint256 maintenanceMargin = posOiInitial.mulUp(marginMaintenance);
        can_ = val < maintenanceMargin;
    }

    /// @notice Computes the liquidation price of a position
    /// @dev price when value = maintenance margin
    function liquidationPrice(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 marginMaintenance
    ) internal pure returns (uint256 liqPrice_) {
        uint256 posOiCurrent = oiCurrent(self, ONE, totalOi, totalOiShares);
        uint256 posOiInitial = oiInitial(self, ONE);
        uint256 posDebt = debtCurrent(self, ONE);

        if (self.liquidated || posOiInitial == 0 || posOiCurrent == 0) {
            // return 0 if already liquidated or no oi left in position
            return 0;
        }

        uint256 oiFrame = posOiInitial.mulUp(marginMaintenance).add(posDebt).divDown(posOiCurrent);

        if (self.isLong) {
            liqPrice_ = self.entryPrice.mulUp(oiFrame);
        } else {
            liqPrice_ = self.entryPrice.mulUp((2 * ONE).sub(oiFrame));
        }
    }
}
