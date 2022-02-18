// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";
import "./FixedPoint.sol";

library Position {
    using FixedPoint for uint256;
    uint256 internal constant ONE = 1e18;

    struct Info {
        uint120 notional; // initial notional = collateral * leverage
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

    /// @notice Computes the position's initial notional cast to uint256
    function _notional(Info memory self) private pure returns (uint256) {
        return uint256(self.notional);
    }

    /// @notice Computes the position's initial open interest cast to uint256
    /// @dev shares of open interest = initial notional / entry price
    function _oiShares(Info memory self) private pure returns (uint256) {
        return _notional(self).divDown(self.entryPrice);
    }

    /// @notice Computes the position's debt cast to uint256
    function _debt(Info memory self) private pure returns (uint256) {
        return uint256(self.debt);
    }

    /// @notice Whether the position exists
    /// @dev Is false if position has been liquidated or has zero oi
    function exists(Info memory self) internal pure returns (bool exists_) {
        return (!self.liquidated && self.notional > 0);
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the current shares of open interest position holds
    /// @notice on pos.isLong side of the market
    function oiSharesCurrent(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _oiShares(self).mulDown(fraction);
    }

    /// @notice Computes the current debt position holds
    function debtCurrent(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _debt(self).mulDown(fraction);
    }

    /// @notice Computes the initial notional of position when built
    function notionalInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _notional(self).mulDown(fraction);
    }

    /// @notice Computes the initial open interest of position when built
    function oiInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        return _oiShares(self).mulDown(fraction);
    }

    /// @notice Computes the current open interest of a position accounting for
    /// @notice potential funding payments between long/short sides
    /// @dev returns zero when oiShares = totalOi = totalOiShares = 0 to avoid
    /// @dev div by zero errors
    function oiCurrent(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares
    ) internal pure returns (uint256) {
        uint256 posOiShares = oiSharesCurrent(self, fraction);
        if (posOiShares == 0 || totalOi == 0) return 0;
        return posOiShares.mulDown(totalOi).divDown(totalOiShares);
    }

    /// @notice Computes the position's cost cast to uint256
    /// WARNING: be careful modifying notional and debt on unwind
    function cost(Info memory self, uint256 fraction) internal pure returns (uint256) {
        uint256 posNotionalInitial = notionalInitial(self, fraction);
        uint256 posDebt = debtCurrent(self, fraction);

        // should always be > 0 but use Math.min to be safe w reverts
        uint256 posCost = posNotionalInitial;
        posCost -= Math.min(posCost, posDebt);
        return posCost;
    }

    /// @notice Computes the value of a position
    /// @dev Floors to zero, so won't properly compute if self is underwater
    function value(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff
    ) internal pure returns (uint256 val_) {
        uint256 posOi = oiCurrent(self, fraction, totalOi, totalOiShares);
        uint256 posDebt = debtCurrent(self, fraction);
        uint256 entryPrice = self.entryPrice;

        if (self.isLong) {
            // oi * entryPrice - debt + oi * entryPrice * min(ratioPrice - 1, capPayoff)
            // = oi * entryPrice - debt + oi * entryPrice * [min(ratioPrice, 1 + capPayoff) - 1]
            // = min(oi * currentPrice, oi * entryPrice * (1 + capPayoff)) - debt
            val_ = posOi.mulUp(currentPrice);
            val_ = Math.min(val_, posOi.mulUp(entryPrice).mulUp(ONE + capPayoff));
            val_ -= Math.min(val_, posDebt); // floor to 0
        } else {
            // NOTE: capPayoff >= 1, so no need to include w short
            // oi * entryPrice - debt - oi * (currentPrice - entryPrice)
            // = 2 * oi * entryPrice - [ debt + oi * currentPrice ]
            val_ = posOi.mulUp(2 * entryPrice);
            // floor to 0
            val_ -= Math.min(val_, posDebt + posOi.mulDown(currentPrice));
        }
    }

    /// @notice Computes the current notional of a position including PnL
    /// @dev Floors to debt if value <= 0
    function notionalCurrent(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff
    ) internal pure returns (uint256 notional_) {
        uint256 posValue = value(self, fraction, totalOi, totalOiShares, currentPrice, capPayoff);
        uint256 posDebt = debtCurrent(self, fraction);
        notional_ = posValue + posDebt;
    }

    /// @notice Computes the trading fees to be imposed on a position for build/unwind
    function tradingFee(
        Info memory self,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 tradingFeeRate
    ) internal pure returns (uint256 tradingFee_) {
        uint256 posNotional = notionalCurrent(
            self,
            fraction,
            totalOi,
            totalOiShares,
            currentPrice,
            capPayoff
        );
        tradingFee_ = posNotional.mulDown(tradingFeeRate);
    }

    /// @notice Whether a position can be liquidated
    /// @dev is true when value < maintenance margin
    function liquidatable(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 maintenanceMarginFraction
    ) internal pure returns (bool can_) {
        uint256 fraction = ONE;
        uint256 posNotionalInitial = notionalInitial(self, fraction);

        if (self.liquidated || posNotionalInitial == 0) {
            // already been liquidated
            return false;
        }

        uint256 val = value(self, fraction, totalOi, totalOiShares, currentPrice, capPayoff);
        uint256 maintenanceMargin = posNotionalInitial.mulDown(maintenanceMarginFraction);
        can_ = val < maintenanceMargin;
    }

    /// @notice Computes the liquidation price of a position
    /// @dev price when value = maintenance margin
    function liquidationPrice(
        Info memory self,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 maintenanceMarginFraction
    ) internal pure returns (uint256 liqPrice_) {
        uint256 fraction = ONE;
        uint256 posOiCurrent = oiCurrent(self, fraction, totalOi, totalOiShares);
        uint256 posNotionalInitial = notionalInitial(self, fraction);
        uint256 posDebt = debtCurrent(self, fraction);

        if (self.liquidated || posNotionalInitial == 0 || posOiCurrent == 0) {
            // return 0 if already liquidated or no oi left in position
            return 0;
        }

        if (self.isLong) {
            // liqPrice = (debt + mm * notionalInitial) / oiCurrent
            liqPrice_ = posNotionalInitial.mulDown(maintenanceMarginFraction).add(posDebt).divDown(
                posOiCurrent
            );
        } else {
            // liqPrice = 2 * entryPrice - (debt + mm * notionalInitial) / oiCurrent
            liqPrice_ = 2 * self.entryPrice;
            // floor to zero
            liqPrice_ -= Math.min(
                liqPrice_,
                posNotionalInitial.mulDown(maintenanceMarginFraction).add(posDebt).divDown(
                    posOiCurrent
                )
            );
        }
    }
}
