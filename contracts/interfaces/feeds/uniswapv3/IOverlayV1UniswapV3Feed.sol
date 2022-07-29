// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../IOverlayV1Feed.sol";

interface IOverlayV1UniswapV3Feed is IOverlayV1Feed {
    function marketPool() external view returns (address);

    function ovlXPool() external view returns (address);

    function marketToken0() external view returns (address);

    function marketToken1() external view returns (address);

    function marketBaseToken() external view returns (address);

    function marketQuoteToken() external view returns (address);

    function marketBaseAmount() external view returns (uint128);

    function ovl() external view returns (address);

    // @dev X is the common token between marketPool and ovlXPool
    function x() external view returns (address);

    // COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    function consult(
        address pool,
        uint32[] memory secondsAgos,
        uint32[] memory windows,
        uint256[] memory nowIdxs
    )
        external
        view
        returns (int24[] memory arithmeticMeanTicks_, uint128[] memory harmonicMeanLiquidities_);

    // COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    function getQuoteAtTick(
        int24 tick,
        uint128 baseAmount,
        address baseToken,
        address quoteToken
    ) external view returns (uint256 quoteAmount_);

    // virtual balance of X in the pool in OVL terms
    function getReserveInOvl(
        int24 arithmeticMeanTickMarket,
        uint128 harmonicMeanLiquidityMarket,
        int24 arithmeticMeanTickOvlX
    ) external view returns (uint256 reserveInOvl_);

    // virtual balance of X in the pool
    function getReserveInX(int24 arithmeticMeanTickMarket, uint128 harmonicMeanLiquidityMarket)
        external
        view
        returns (uint256 reserveInX_);
}
