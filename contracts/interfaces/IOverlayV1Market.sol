// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../libraries/Oracle.sol";
import "../libraries/Risk.sol";
import "../libraries/Roller.sol";

import "./IOverlayV1Token.sol";

interface IOverlayV1Market {
    // immutables
    function ovl() external view returns (IOverlayV1Token);

    function feed() external view returns (address);

    function factory() external view returns (address);

    // risk params
    function params(uint256 idx) external view returns (uint256);

    // oi related quantities
    function oiLong() external view returns (uint256);

    function oiShort() external view returns (uint256);

    function oiLongShares() external view returns (uint256);

    function oiShortShares() external view returns (uint256);

    // rollers
    function snapshotVolumeBid()
        external
        view
        returns (
            uint32 timestamp_,
            uint32 window_,
            int192 accumulator_
        );

    function snapshotVolumeAsk()
        external
        view
        returns (
            uint32 timestamp_,
            uint32 window_,
            int192 accumulator_
        );

    function snapshotMinted()
        external
        view
        returns (
            uint32 timestamp_,
            uint32 window_,
            int192 accumulator_
        );

    // positions
    function positions(bytes32 key)
        external
        view
        returns (
            uint96 notionalInitial_,
            uint96 debtInitial_,
            int24 midTick_,
            int24 entryTick_,
            bool isLong_,
            bool liquidated_,
            uint240 oiShares_,
            uint16 fractionRemaining_
        );

    // update related quantities
    function timestampUpdateLast() external view returns (uint256);

    // cached risk calcs
    function dpUpperLimit() external view returns (uint256);

    // emergency shutdown
    function isShutdown() external view returns (bool);

    // initializes market
    function initialize(uint256[15] memory params) external;

    // position altering functions
    function build(
        uint256 collateral,
        uint256 leverage,
        bool isLong,
        uint256 priceLimit
    ) external returns (uint256 positionId_);

    function unwind(
        uint256 positionId,
        uint256 fraction,
        uint256 priceLimit
    ) external;

    function liquidate(address owner, uint256 positionId) external;

    // updates market
    function update() external returns (Oracle.Data memory);

    // sanity check on data fetched from oracle in case of manipulation
    function dataIsValid(Oracle.Data memory) external view returns (bool);

    // current open interest after funding payments transferred
    function oiAfterFunding(
        uint256 oiOverweight,
        uint256 oiUnderweight,
        uint256 timeElapsed
    ) external view returns (uint256 oiOverweight_, uint256 oiUnderweight_);

    // current open interest cap with adjustments for circuit breaker if market has
    // printed a lot in recent past
    function capOiAdjustedForCircuitBreaker(uint256 cap) external view returns (uint256);

    // bound on open interest cap from circuit breaker
    function circuitBreaker(Roller.Snapshot memory snapshot, uint256 cap)
        external
        view
        returns (uint256);

    // current notional cap with adjustments to prevent front-running
    // trade and back-running trade
    function capNotionalAdjustedForBounds(Oracle.Data memory data, uint256 cap)
        external
        view
        returns (uint256);

    // bound on open interest cap to mitigate front-running attack
    function frontRunBound(Oracle.Data memory data) external view returns (uint256);

    // bound on open interest cap to mitigate back-running attack
    function backRunBound(Oracle.Data memory data) external view returns (uint256);

    // transforms notional into number of contracts (open interest)
    function oiFromNotional(uint256 notional, uint256 midPrice) external view returns (uint256);

    // bid price given oracle data and recent volume
    function bid(Oracle.Data memory data, uint256 volume) external view returns (uint256 bid_);

    // ask price given oracle data and recent volume
    function ask(Oracle.Data memory data, uint256 volume) external view returns (uint256 ask_);

    // risk parameter setter
    function setRiskParam(Risk.Parameters name, uint256 value) external;

    // emergency shutdown market
    function shutdown() external;

    // emergency withdraw collateral after shutdown
    function emergencyWithdraw(uint256 positionId) external;
}
