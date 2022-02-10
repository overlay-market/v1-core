// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "./IOverlayV1Token.sol";

interface IOverlayV1Market {
    // immutables
    function ovl() external view returns (IOverlayV1Token);

    function feed() external view returns (address);

    function factory() external view returns (address);

    // risk params
    function k() external view returns (uint256);

    function lmbda() external view returns (uint256);

    function delta() external view returns (uint256);

    function capPayoff() external view returns (uint256);

    function capOi() external view returns (uint256);

    function capLeverage() external view returns (uint256);

    function circuitBreakerWindow() external view returns (uint256);

    function circuitBreakerMintTarget() external view returns (uint256);

    function maintenanceMargin() external view returns (uint256);

    function maintenanceMarginBurnRate() external view returns (uint256);

    function tradingFeeRate() external view returns (uint256);

    function minCollateral() external view returns (uint256);

    function priceDriftUpperLimit() external view returns (uint256);

    // trading fee related quantities
    function tradingFeeRecipient() external view returns (address);

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
            uint120 oiShares_,
            uint120 debt_,
            bool isLong_,
            bool liquidated_,
            uint256 entryPrice_
        );

    // update related quantities
    function timestampUpdateLast() external view returns (uint256);
}
