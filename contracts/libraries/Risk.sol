// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

library Risk {
    enum Parameters {
        K, // funding constant
        Lmbda, // market impact constant
        Delta, // bid-ask static spread constant
        CapPayoff, // payoff cap
        CapNotional, // initial notional cap
        CapLeverage, // initial leverage cap
        CircuitBreakerWindow, // trailing window for circuit breaker
        CircuitBreakerMintTarget, // target worst case inflation rate over trailing window
        MaintenanceMarginFraction, // maintenance margin (mm) constant
        MaintenanceMarginBurnRate, // burn rate for mm constant
        LiquidationFeeRate, // liquidation fee charged on liquidate
        TradingFeeRate, // trading fee charged on build/unwind
        MinCollateral, // minimum ovl collateral to open position
        PriceDriftUpperLimit, // upper limit for feed price changes since last update
        AverageBlockTime // average block time of the respective chain
    }

    /// @notice Gets the value associated with the given parameter type
    function get(uint256[15] storage self, Parameters name) internal view returns (uint256) {
        return self[uint256(name)];
    }

    /// @notice Sets the value associated with the given parameter type
    function set(
        uint256[15] storage self,
        Parameters name,
        uint256 value
    ) internal {
        self[uint256(name)] = value;
    }
}
