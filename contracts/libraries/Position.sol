// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "./FixedPoint.sol";
import "./FixedPoint96.sol";
import "./FixedPoint160.sol";
import "./FixedPoint192.sol";

library Position {
    using FixedPoint for uint256;
    uint256 internal constant ONE = 1e18;

    struct Info {
        uint88 notional; // initial notional = collateral * leverage
        bool isLong; // whether long or short
        uint160 entryPrice; // price received at entry
        uint88 debt; // debt
        bool liquidated; // whether has been liquidated
        uint160 midPrice; // mid price at entry; used to calculate oi shares
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION UTIL FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Calculates number of contracts (oi) for a given notional and price
    /// @dev left shifted x160 to avoid truncation, reverts on price == 0
    /// @dev notional values bounded: 2e12 (~2**40) < notional < 8e24 (~2**88) from factory
    /// @dev price is always < FixedPoint160.Q160 since uint160 originally
    // TODO: test
    function oiX160FromNotional(uint256 notional, uint256 price) internal pure returns (uint256) {
        // NOTE: range of values for oi are ~ 2**-120 < oi < 2**88 (we use effectively 96.160)
        // NOTE: range of values for oiX160 are ~ 2**40 < oiX160 < 2**248
        return (notional << FixedPoint160.RESOLUTION) / price;
    }

    /// @notice Calculates the notional size of a given number of contracts (oi)
    /// @notice at the given price
    /// @dev price is always < FixedPoint160.Q160 since uint160 originally
    // TODO: test, rigorously
    function notionalFromOiX160(uint256 oiX160, uint256 price) internal pure returns (uint256) {
        if (oiX160 == 0 || price == 0) {
            return 0;
        }

        // TODO: test and check for the edge cases (bound min/max)
        if (oiX160 < FixedPoint96.Q96) {
            // oiX160: [1, 2**96]
            // price: [1, 2**160]
            // notional: [1, 2**96]
            return (oiX160 * price) >> FixedPoint160.RESOLUTION;
        } else if (oiX160 < FixedPoint160.Q160 && price < FixedPoint96.Q96) {
            // oiX160: [2**96, 2**160]
            // price: [1, 2**96]
            // notional: [1, 2**96]
            return (oiX160 * price) >> FixedPoint160.RESOLUTION;
        } else if (oiX160 < FixedPoint160.Q160 && price >= FixedPoint96.Q96) {
            // oiX160: [2**96, 2**160]
            // price: [2**96, 2**160]
            // notional: [2**32, 2**160]
            uint256 inversePrice = (1 << FixedPoint160.RESOLUTION).divDown(price);
            return oiX160.divDown(inversePrice);
        } else if (oiX160 < FixedPoint192.Q192 && price < FixedPoint96.Q96) {
            // oiX160: [2**160, 2**192]
            // price: [1, 2**96]
            // notional: [1, 2**128]
            uint256 inversePrice = (1 << FixedPoint160.RESOLUTION).divDown(price);
            return oiX160.divDown(inversePrice);
        } else if (oiX160 < FixedPoint192.Q192 && price >= FixedPoint96.Q96) {
            // oiX160: [2**160, 2**192]
            // price: [2**96, 2**160]
            // notional: [2**96, 2**192]
            uint256 inversePrice = (1 << FixedPoint160.RESOLUTION).divDown(price);
            return oiX160.divDown(inversePrice);
        } else {
            // oiX160: [2**192, 2**256]
            // price: [1, 2**160]
            // notional: [1, 2**256]
            return (oiX160 >> FixedPoint160.RESOLUTION) * price;
        }
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
                    POSITION CAST GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the position's initial notional cast to uint256
    function _notional(Info memory self) private pure returns (uint256) {
        return uint256(self.notional);
    }

    /// @notice Computes the position's initial open interest cast to uint256
    function _oiX160Shares(Info memory self) private pure returns (uint256) {
        return oiX160FromNotional(self.notional, _midPrice(self));
    }

    /// @notice Computes the position's debt cast to uint256
    function _debt(Info memory self) private pure returns (uint256) {
        return uint256(self.debt);
    }

    /// @notice Computes the position's entry price cast to uint256
    // TODO: test
    function _entryPrice(Info memory self) private pure returns (uint256) {
        return uint256(self.entryPrice);
    }

    /// @notice Computes the position's mid price at entry cast to uint256
    // TODO: test
    function _midPrice(Info memory self) private pure returns (uint256) {
        return uint256(self.midPrice);
    }

    /// @notice Whether the position exists
    /// @dev Is false if position has been liquidated or has zero oi
    function exists(Info memory self) internal pure returns (bool exists_) {
        return (!self.liquidated && self.notional > 0);
    }

    /*///////////////////////////////////////////////////////////////
                POSITION FRACTIONAL GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Computes the initial notional of position when built
    /// @dev use mulUp to avoid rounding leftovers on unwind
    function notionalInitial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        require(fraction <= ONE, "Position:fraction>max");
        return _notional(self).mulUp(fraction);
    }

    /// @notice Computes the initial open interest of position when built
    /// @dev use mulUp to avoid rounding leftovers on unwind
    // TODO: test
    function oiX160Initial(Info memory self, uint256 fraction) internal pure returns (uint256) {
        require(fraction <= ONE, "Position:fraction>max");

        // careful with overflow given fraction max is ONE = 1e18 (~ 2**60)
        uint256 oiX160 = _oiX160Shares(self);
        if (oiX160 >= FixedPoint192.Q192) {
            uint256 inverseFraction = ONE.divUp(fraction);
            return oiX160.divUp(inverseFraction);
        }
        return oiX160.mulUp(fraction);
    }

    /// @notice Computes the current debt position holds
    /// @dev use mulUp to avoid rounding leftovers on unwind
    function debtCurrent(Info memory self, uint256 fraction) internal pure returns (uint256) {
        require(fraction <= ONE, "Position:fraction>max");
        return _debt(self).mulUp(fraction);
    }

    /// @notice Computes the current shares of open interest position holds
    /// @notice on pos.isLong side of the market
    /// @dev use mulUp to avoid rounding leftovers on unwind
    // TODO: test
    function oiX160SharesCurrent(Info memory self, uint256 fraction)
        internal
        pure
        returns (uint256)
    {
        return oiX160Initial(self, fraction);
    }

    /// @notice Computes the current open interest of a position accounting for
    /// @notice potential funding payments between long/short sides
    /// @dev returns zero when oiShares = oiTotalOnSide = oiTotalSharesOnSide = 0 to avoid
    /// @dev div by zero errors
    /// @dev use mulUp, divUp to avoid rounding leftovers on unwind
    // TODO: test
    function oiX160Current(
        Info memory self,
        uint256 fraction,
        uint256 oiX160TotalOnSide,
        uint256 oiX160TotalSharesOnSide
    ) internal pure returns (uint256) {
        require(fraction <= ONE, "Position:fraction>max");

        // NOTE: pos.oiX160SharesCurrent <= oiX160TotalSharesOnSide always
        // enforce with Math.min in case of rounding errors
        uint256 posOiX160Shares = oiX160SharesCurrent(self, fraction);
        posOiX160Shares = Math.min(posOiX160Shares, oiX160TotalSharesOnSide);

        // check the zero edge cases
        if (posOiX160Shares == 0 || oiX160TotalSharesOnSide == 0 || oiX160TotalOnSide == 0) {
            return 0;
        }

        // calculate fraction of oi shares this position has
        // careful with overflow given divUp inflates by ONE = 1e18 (~ 2**60)
        uint256 fractionOiX160Shares;
        if (oiX160TotalSharesOnSide >= FixedPoint192.Q192) {
            uint256 posOiShares = (posOiX160Shares >> FixedPoint160.RESOLUTION);
            uint256 oiTotalSharesOnSide = (oiX160TotalSharesOnSide >> FixedPoint160.RESOLUTION);
            fractionOiX160Shares = posOiShares.divDown(oiTotalSharesOnSide);
        } else {
            fractionOiX160Shares = posOiX160Shares.divUp(oiX160TotalSharesOnSide);
        }

        // multiple fraction of oi shares position has with total oi on side
        // careful with overflow given fractionOiX160Shares max is ONE = 1e18 (~ 2**60)
        if (oiX160TotalOnSide >= FixedPoint192.Q192) {
            uint256 inverseFractionOiX160Shares = ONE.divUp(fractionOiX160Shares);
            return oiX160TotalOnSide.divUp(inverseFractionOiX160Shares);
        }
        return oiX160TotalOnSide.mulUp(fractionOiX160Shares);
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

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

    /// @notice Computes the position's current collateral cast to uint256
    /// @dev Floors to zero, so won't properly compute if self is underwater
    function collateral(
        Info memory self,
        uint256 fraction,
        uint256 oiX160TotalOnSide,
        uint256 oiX160TotalSharesOnSide
    ) internal pure returns (uint256 collateral_) {
        // N(t) = OI(t) * MP(0) - D; where MP(0) = Q(0) / OI(0) is self.midPrice
        uint256 posOiX160Current = oiX160Current(
            self,
            fraction,
            oiX160TotalOnSide,
            oiX160TotalSharesOnSide
        );
        uint256 posDebt = debtCurrent(self, fraction); // D
        uint256 midPrice = _midPrice(self);

        // OI(t) * MP(0)
        collateral_ = notionalFromOiX160(posOiX160Current, midPrice);

        // subtract off the debt
        // use Math.min to floor to zero in case underwater
        collateral_ -= Math.min(collateral_, posDebt);
    }

    /// @notice Computes the value of a position
    /// @dev Floors to zero, so won't properly compute if self is underwater
    // TODO: test
    function value(
        Info memory self,
        uint256 fraction,
        uint256 oiX160TotalOnSide,
        uint256 oiX160TotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff
    ) internal pure returns (uint256 val_) {
        // V(t) = Q(0) * (OI(t) / OI(0)) - D +/- OI(t) * [P(t) - P(0)]
        //      = N(t) +/- OI(t) * [P(t) - P(0)]
        uint256 posCollateral = collateral(
            self,
            fraction,
            oiX160TotalOnSide,
            oiX160TotalSharesOnSide
        );
        uint256 posOiX160Current = oiX160Current(
            self,
            fraction,
            oiX160TotalOnSide,
            oiX160TotalSharesOnSide
        );
        uint256 entryPrice = _entryPrice(self); // P(0)

        // start with the collateral: N(t)
        val_ = posCollateral;

        // pnl calc to add to/subtract from collateral: +/- OI(t) * [P(t) - P(0)]
        if (self.isLong && currentPrice > entryPrice) {
            // v += OI * [P(t) - P(0)]
            uint256 dp = currentPrice - entryPrice;
            // cap the payoff
            if (dp > entryPrice.mulUp(capPayoff)) dp = entryPrice.mulUp(capPayoff);
            uint256 pnl = notionalFromOiX160(posOiX160Current, dp);
            val_ += pnl;
        } else if (self.isLong && currentPrice <= entryPrice) {
            // v -= OI * [P(0) - P(t)]
            uint256 dp = entryPrice - currentPrice;
            uint256 pnl = notionalFromOiX160(posOiX160Current, dp);
            val_ -= Math.min(val_, pnl); // floor to zero
        } else if (!self.isLong && currentPrice > entryPrice) {
            // v -= OI * [P(t) - P(0)]
            uint256 dp = currentPrice - entryPrice;
            // cap the payoff
            if (dp > entryPrice.mulUp(capPayoff)) dp = entryPrice.mulUp(capPayoff);
            uint256 pnl = notionalFromOiX160(posOiX160Current, dp);
            val_ -= Math.min(val_, pnl);
        } else {
            // v += OI * [P(0) - P(t)]
            uint256 dp = entryPrice - currentPrice;
            uint256 pnl = notionalFromOiX160(posOiX160Current, dp);
            val_ += pnl;
        }
    }

    /// @notice Computes the current notional of a position including PnL
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
        uint256 posDebt = debtCurrent(self, fraction);
        notionalWithPnl_ = posValue + posDebt;
    }

    /// @notice Computes the trading fees to be imposed on a position for build/unwind
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
    /// @dev is true when value < maintenance margin
    function liquidatable(
        Info memory self,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
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

        uint256 val = value(
            self,
            fraction,
            oiTotalOnSide,
            oiTotalSharesOnSide,
            currentPrice,
            capPayoff
        );
        uint256 maintenanceMargin = posNotionalInitial.mulUp(maintenanceMarginFraction);
        can_ = val < maintenanceMargin;
    }
}
