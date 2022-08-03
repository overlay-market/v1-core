// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "../libraries/uniswap/v3-core/FullMath.sol";
import "./FixedCast.sol";
import "./FixedPoint.sol";
import "./Tick.sol";

library Position {
    using FixedCast for uint16;
    using FixedCast for uint256;
    using FixedPoint for uint256;

    uint256 internal constant ONE = 1e18;

    /// @dev immutables: notionalInitial, debtInitial, midTick, entryTick, isLong
    /// @dev mutables: liquidated, oiShares, fractionRemaining
    struct Info {
        uint96 notionalInitial; // initial notional = collateral * leverage
        uint96 debtInitial; // initial debt = notional - collateral
        int24 midTick; // midPrice = 1.0001 ** midTick at build
        int24 entryTick; // entryPrice = 1.0001 ** entryTick at build
        bool isLong; // whether long or short
        bool liquidated; // whether has been liquidated (mutable)
        uint240 oiShares; // current shares of aggregate open interest on side (mutable)
        uint16 fractionRemaining; // fraction of initial position remaining (mutable)
    }

    /*///////////////////////////////////////////////////////////////
                        POSITIONS MAPPING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Retrieves a position from positions mapping
    function get(
        mapping(bytes32 => Info) storage self,
        address owner,
        uint256 id
    ) internal view returns (Info memory position_) {
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
                    POSITION CAST GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the position's initial notional cast to uint256
    function _notionalInitial(Info memory self) private pure returns (uint256) {
        return uint256(self.notionalInitial);
    }

    /// @notice Computes the position's initial debt cast to uint256
    function _debtInitial(Info memory self) private pure returns (uint256) {
        return uint256(self.debtInitial);
    }

    /// @notice Computes the position's current shares of open interest
    /// @notice cast to uint256
    function _oiShares(Info memory self) private pure returns (uint256) {
        return uint256(self.oiShares);
    }

    /// @notice Computes the fraction remaining of the position cast to uint256
    function _fractionRemaining(Info memory self) private pure returns (uint256) {
        return self.fractionRemaining.toUint256Fixed();
    }

    /*///////////////////////////////////////////////////////////////
                     POSITION EXISTENCE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Whether the position exists
    /// @dev Is false if position has been liquidated or fraction remaining == 0
    function exists(Info memory self) internal pure returns (bool exists_) {
        return (!self.liquidated && self.fractionRemaining > 0);
    }

    /*///////////////////////////////////////////////////////////////
                 POSITION FRACTION REMAINING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Gets the current fraction remaining of the initial position
    function getFractionRemaining(Info memory self) internal pure returns (uint256) {
        return _fractionRemaining(self);
    }

    /// @notice Computes an updated fraction remaining of the initial position
    /// @notice given fractionRemoved unwound/liquidated from remaining position
    function updatedFractionRemaining(Info memory self, uint256 fractionRemoved)
        internal
        pure
        returns (uint16)
    {
        require(fractionRemoved <= ONE, "OVLV1:fraction>max");
        uint256 fractionRemaining = _fractionRemaining(self).mulDown(ONE - fractionRemoved);
        return fractionRemaining.toUint16Fixed();
    }

    /*///////////////////////////////////////////////////////////////
                      POSITION PRICE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the midPrice of the position at entry cast to uint256
    /// @dev Will be slightly different (tol of 1bps) vs actual
    /// @dev midPrice at build given tick resolution limited to 1bps
    /// @dev Only affects value() calc below and thus PnL slightly
    function midPriceAtEntry(Info memory self) internal pure returns (uint256 midPrice_) {
        midPrice_ = Tick.tickToPrice(self.midTick);
    }

    /// @notice Computes the entryPrice of the position cast to uint256
    /// @dev Will be slightly different (tol of 1bps) vs actual
    /// @dev entryPrice at build given tick resolution limited to 1bps
    /// @dev Only affects value() calc below and thus PnL slightly
    function entryPrice(Info memory self) internal pure returns (uint256 entryPrice_) {
        entryPrice_ = Tick.tickToPrice(self.entryTick);
    }

    /*///////////////////////////////////////////////////////////////
                         POSITION OI FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the amount of shares of open interest to issue
    /// @notice a newly built position
    /// @dev use mulDiv
    function calcOiShares(
        uint256 oi,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide
    ) internal pure returns (uint256 oiShares_) {
        oiShares_ = (oiTotalOnSide == 0 || oiTotalSharesOnSide == 0)
            ? oi
            : FullMath.mulDiv(oi, oiTotalSharesOnSide, oiTotalOnSide);
    }

    /// @notice Computes the position's initial open interest cast to uint256
    /// @dev oiInitial = Q / midPriceAtEntry
    /// @dev Will be slightly different (tol of 1bps) vs actual oi at build
    /// @dev given midTick resolution limited to 1bps
    /// @dev Only affects value() calc below and thus PnL slightly
    function _oiInitial(Info memory self) private pure returns (uint256) {
        uint256 q = _notionalInitial(self);
        uint256 mid = midPriceAtEntry(self);
        return q.divDown(mid);
    }

    /*///////////////////////////////////////////////////////////////
                POSITION FRACTIONAL GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the initial notional of position when built
    /// @notice accounting for amount of position remaining
    /// @dev use mulUp to avoid rounding leftovers on unwind
    function notionalInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        uint256 fractionRemaining = _fractionRemaining(self);
        uint256 notionalForRemaining = _notionalInitial(self).mulUp(fractionRemaining);
        return notionalForRemaining.mulUp(fraction);
    }

    /// @notice Computes the initial open interest of position when built
    /// @notice accounting for amount of position remaining
    /// @dev use mulUp to avoid rounding leftovers on unwind
    function oiInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        uint256 fractionRemaining = _fractionRemaining(self);
        uint256 oiInitialForRemaining = _oiInitial(self).mulUp(fractionRemaining);
        return oiInitialForRemaining.mulUp(fraction);
    }

    /// @notice Computes the current shares of open interest position holds
    /// @notice on pos.isLong side of the market
    /// @dev use mulDown to avoid giving excess shares to pos owner on unwind
    function oiSharesCurrent(Info memory self, uint256 fraction) internal pure returns (uint256) {
        uint256 oiSharesForRemaining = _oiShares(self);
        // WARNING: must mulDown to avoid giving excess oi shares
        return oiSharesForRemaining.mulDown(fraction);
    }

    /// @notice Computes the current debt position holds accounting
    /// @notice for amount of position remaining
    /// @dev use mulUp to avoid rounding leftovers on unwind
    function debtInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        uint256 fractionRemaining = _fractionRemaining(self);
        uint256 debtForRemaining = _debtInitial(self).mulUp(fractionRemaining);
        return debtForRemaining.mulUp(fraction);
    }

    /// @notice Computes the current open interest of remaining position accounting for
    /// @notice potential funding payments between long/short sides
    /// @dev returns zero when oiShares = oiTotalOnSide = oiTotalSharesOnSide = 0 to avoid
    /// @dev div by zero errors
    /// @dev use mulDiv
    function oiCurrent(
        Info memory self,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide
    ) internal pure returns (uint256) {
        uint256 oiShares = oiSharesCurrent(self, fraction);
        if (oiShares == 0 || oiTotalOnSide == 0 || oiTotalSharesOnSide == 0) return 0;
        return FullMath.mulDiv(oiShares, oiTotalOnSide, oiTotalSharesOnSide);
    }

    /// @notice Computes the remaining position's cost cast to uint256
    function cost(Info memory self, uint256 fraction) internal pure returns (uint256) {
        uint256 posNotionalInitial = notionalInitial(self, fraction);
        uint256 posDebt = debtInitial(self, fraction);

        // should always be > 0 but use subFloor to be safe w reverts
        uint256 posCost = posNotionalInitial;
        posCost = posCost.subFloor(posDebt);
        return posCost;
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the value of remaining position
    /// @dev Floors to zero, so won't properly compute if self is underwater
    function value(
        Info memory self,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff
    ) internal pure returns (uint256 val_) {
        uint256 posOiInitial = oiInitial(self, fraction);
        uint256 posNotionalInitial = notionalInitial(self, fraction);
        uint256 posDebt = debtInitial(self, fraction);

        uint256 posOiCurrent = oiCurrent(self, fraction, oiTotalOnSide, oiTotalSharesOnSide);
        uint256 posEntryPrice = entryPrice(self);

        // NOTE: PnL = +/- oiCurrent * [currentPrice - entryPrice]; ... (w/o capPayoff)
        // NOTE: fundingPayments = notionalInitial * ( oiCurrent / oiInitial - 1 )
        // NOTE: value = collateralInitial + PnL + fundingPayments
        // NOTE:       = notionalInitial - debt + PnL + fundingPayments
        if (self.isLong) {
            // val = notionalInitial * oiCurrent / oiInitial
            //       + oiCurrent * min[currentPrice, entryPrice * (1 + capPayoff)]
            //       - oiCurrent * entryPrice - debt
            val_ =
                posNotionalInitial.mulUp(posOiCurrent).divUp(posOiInitial) +
                Math.min(
                    posOiCurrent.mulUp(currentPrice),
                    posOiCurrent.mulUp(posEntryPrice).mulUp(ONE + capPayoff)
                );
            // floor to 0
            val_ = val_.subFloor(posDebt + posOiCurrent.mulUp(posEntryPrice));
        } else {
            // NOTE: capPayoff >= 1, so no need to include w short
            // val = notionalInitial * oiCurrent / oiInitial + oiCurrent * entryPrice
            //       - oiCurrent * currentPrice - debt
            val_ =
                posNotionalInitial.mulUp(posOiCurrent).divUp(posOiInitial) +
                posOiCurrent.mulUp(posEntryPrice);
            // floor to 0
            val_ = val_.subFloor(posDebt + posOiCurrent.mulUp(currentPrice));
        }
    }

    /// @notice Computes the current notional of remaining position including PnL
    /// @dev Floors to debt if value <= 0
    function notionalWithPnl(
        Info memory self,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff
    ) internal pure returns (uint256 notionalWithPnl_) {
        uint256 posValue = value(
            self,
            fraction,
            oiTotalOnSide,
            oiTotalSharesOnSide,
            currentPrice,
            capPayoff
        );
        uint256 posDebt = debtInitial(self, fraction);
        notionalWithPnl_ = posValue + posDebt;
    }

    /// @notice Computes the trading fees to be imposed on remaining position
    /// @notice for build/unwind
    function tradingFee(
        Info memory self,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 tradingFeeRate
    ) internal pure returns (uint256 tradingFee_) {
        uint256 posNotional = notionalWithPnl(
            self,
            fraction,
            oiTotalOnSide,
            oiTotalSharesOnSide,
            currentPrice,
            capPayoff
        );
        tradingFee_ = posNotional.mulUp(tradingFeeRate);
    }

    /// @notice Whether a position can be liquidated
    /// @dev is true when value * (1 - liq fee rate) < maintenance margin
    /// @dev liq fees are reward given to liquidator
    function liquidatable(
        Info memory self,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 maintenanceMarginFraction,
        uint256 liquidationFeeRate
    ) internal pure returns (bool can_) {
        uint256 fraction = ONE;
        uint256 posNotionalInitial = notionalInitial(self, fraction);

        if (self.liquidated || self.fractionRemaining == 0) {
            // already been liquidated or doesn't exist
            // latter covers edge case of val == 0 and MM + liq fee == 0
            return false;
        }

        uint256 val = value(
            self,
            fraction,
            oiTotalOnSide,
            oiTotalSharesOnSide,
            currentPrice,
            capPayoff
        );
        uint256 maintenanceMargin = posNotionalInitial.mulUp(maintenanceMarginFraction);
        uint256 liquidationFee = val.mulDown(liquidationFeeRate);
        can_ = val < maintenanceMargin + liquidationFee;
    }
}
