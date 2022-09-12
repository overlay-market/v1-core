// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../IOverlayV1Feed.sol";

interface IOverlayV1NoReserveUniswapV3Feed is IOverlayV1Feed {
    function marketPool() external view returns (address);

    function marketToken0() external view returns (address);

    function marketToken1() external view returns (address);

    function marketBaseToken() external view returns (address);

    function marketQuoteToken() external view returns (address);

    function marketBaseAmount() external view returns (uint128);

    // COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    function consult(
        address pool,
        uint32[] memory secondsAgos,
        uint32[] memory windows,
        uint256[] memory nowIdxs
    ) external view returns (int24[] memory arithmeticMeanTicks_);

    // COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    function getQuoteAtTick(
        int24 tick,
        uint128 baseAmount,
        address baseToken,
        address quoteToken
    ) external view returns (uint256 quoteAmount_);
}
