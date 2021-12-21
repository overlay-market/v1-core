// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.10;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

// forks of uniswap libraries for solidity^0.8.10
import "../../libraries/uniswap/v3-core/FullMath.sol";
import "../../libraries/uniswap/v3-core/TickMath.sol";

import "../OverlayV1Feed.sol";

contract OverlayV1UniswapV3Feed is OverlayV1Feed {
    address constant public WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    uint128 internal constant ONE = 1e18; // 18 decimal places for ovl

    address immutable public marketPool;
    address immutable public ovlWethPool;
    address immutable public ovl;

    address immutable public marketToken0;
    address immutable public marketToken1;
    address immutable public ovlWethToken0;
    address immutable public ovlWethToken1;

    address immutable public marketBaseToken;
    address immutable public marketQuoteToken;
    uint128 immutable public marketBaseAmount;

    constructor(
        address _marketPool,
        address _ovlWethPool,
        address _ovl,
        address _marketBaseToken,
        address _marketQuoteToken,
        uint128 _marketBaseAmount,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        // need WETH in market pool to make reserve conversion from ETH => OVL
        address _marketToken0 = IUniswapV3Pool(_marketPool).token0();
        address _marketToken1 = IUniswapV3Pool(_marketPool).token1();

        require(_marketToken0 == WETH || _marketToken1 == WETH, "OVLV1Feed: marketToken != WETH");
        marketToken0 = _marketToken0;
        marketToken1 = _marketToken1;

        require(_marketToken0 == _marketBaseToken || _marketToken1 == _marketBaseToken, "OVLV1Feed: marketToken != marketBaseToken");
        require(_marketToken0 == _marketQuoteToken || _marketToken1 == _marketQuoteToken, "OVLV1Feed: marketToken != marketQuoteToken");
        marketBaseToken = _marketBaseToken;
        marketQuoteToken = _marketQuoteToken;
        marketBaseAmount = _marketBaseAmount;

        address _ovlWethToken0 = IUniswapV3Pool(_ovlWethPool).token0();
        address _ovlWethToken1 = IUniswapV3Pool(_ovlWethPool).token1();

        require(_ovlWethToken0 == WETH || _ovlWethToken1 == WETH, "OVLV1Feed: ovlWethToken != WETH");
        require(_ovlWethToken0 == _ovl || _ovlWethToken1 == _ovl, "OVLV1Feed: ovlWethToken != OVL");
        ovlWethToken0 = _ovlWethToken0;
        ovlWethToken1 = _ovlWethToken1;

        marketPool = _marketPool;
        ovlWethPool = _ovlWethPool;
        ovl = _ovl;
    }

    /// @dev fetches TWAP, liquidity data from the univ3 pool oracle
    /// for micro and macro window averaging intervals
    function _fetch() internal virtual override returns (Oracle.Data memory) {
        uint32[] memory secondsAgos = new uint32[](3);
        secondsAgos[0] = uint32(macroWindow);
        secondsAgos[1] = uint32(microWindow);
        secondsAgos[2] = 0;

        (int24[2] memory arithmeticMeanTicksMarket, uint128[2] memory harmonicMeanLiquiditiesMarket) =
            consult(marketPool, secondsAgos);
        (int24[2] memory arithmeticMeanTicksOvlWeth, uint128[2] memory harmonicMeanLiquiditiesOvlWeth) =
            consult(ovlWethPool, secondsAgos);

        uint256[2] memory prices;
        uint256[2] memory reserves;
        for (uint256 i=0; i < 2; i++) {
            uint256 price = getQuoteAtTick(
                arithmeticMeanTicksMarket[i],
                marketBaseAmount,
                marketBaseToken,
                marketQuoteToken
            );

            uint256 reserve = getReserveInOvl(
                arithmeticMeanTicksMarket[i],
                harmonicMeanLiquiditiesMarket[i],
                arithmeticMeanTicksOvlWeth[i]
            );

            prices[i] = price;
            reserves[i] = reserve;
        }

        // TODO: _checkData();
        return Oracle.Data({
            timestamp: block.timestamp,
            microWindow: microWindow,
            macroWindow: macroWindow,
            priceOverMicroWindow: prices[1],
            priceOverMacroWindow: prices[0],
            reservesOverMicroWindow: reserves[1],
            reservesOverMacroWindow: reserves[0]
        });
    }

    // TODO: function _checkData(Oracle.Data memory data) to verify price is ok with require() statement

    /// @dev COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    function consult(address pool, uint32[] memory secondsAgos) public view returns (
        int24[2] memory arithmeticMeanTicks_,
        uint128[2] memory harmonicMeanLiquidities_
    ) {
        // TODO: test this extensively
        (int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s) =
            IUniswapV3Pool(pool).observe(secondsAgos);

        for (uint256 i=0; i < secondsAgos.length-1; i++) {
            uint32 secondsAgo = secondsAgos[i];

            int56 tickCumulativesDelta = tickCumulatives[secondsAgos.length-1] - tickCumulatives[i];
            uint160 secondsPerLiquidityCumulativesDelta =
                secondsPerLiquidityCumulativeX128s[secondsAgos.length-1] - secondsPerLiquidityCumulativeX128s[i];

            int24 arithmeticMeanTick = int24(tickCumulativesDelta / int56(int32(secondsAgo)));
            // Always round to negative infinity
            if (tickCumulativesDelta < 0 && (tickCumulativesDelta % int56(int32(secondsAgo)) != 0)) arithmeticMeanTick--;

            // We are multiplying here instead of shifting to ensure that harmonicMeanLiquidity doesn't overflow uint128
            uint192 secondsAgoX160 = uint192(secondsAgo) * type(uint160).max;
            uint128 harmonicMeanLiquidity = uint128(secondsAgoX160 / (uint192(secondsPerLiquidityCumulativesDelta) << 32));

            arithmeticMeanTicks_[i] = arithmeticMeanTick;
            harmonicMeanLiquidities_[i] = harmonicMeanLiquidity;
        }
    }

    /// @dev COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    function getQuoteAtTick(
        int24 tick,
        uint128 baseAmount,
        address baseToken,
        address quoteToken
    ) public view returns (uint256 quoteAmount_) {
        uint160 sqrtRatioX96 = TickMath.getSqrtRatioAtTick(tick);

        // Calculate quoteAmount with better precision if it doesn't overflow when multiplied by itself
        if (sqrtRatioX96 <= type(uint128).max) {
            uint256 ratioX192 = uint256(sqrtRatioX96) * sqrtRatioX96;
            quoteAmount_ = baseToken < quoteToken
                ? FullMath.mulDiv(ratioX192, baseAmount, 1 << 192)
                : FullMath.mulDiv(1 << 192, baseAmount, ratioX192);
        } else {
            uint256 ratioX128 = FullMath.mulDiv(sqrtRatioX96, sqrtRatioX96, 1 << 64);
            quoteAmount_ = baseToken < quoteToken
                ? FullMath.mulDiv(ratioX128, baseAmount, 1 << 128)
                : FullMath.mulDiv(1 << 128, baseAmount, ratioX128);
        }
    }

    function getReserveInOvl(
        int24 arithmeticMeanTickMarket,
        uint128 harmonicMeanLiquidityMarket,
        int24 arithmeticMeanTickOvlWeth
    ) public view returns (uint256 reserveInOvl_) {
        // TODO: test this extensively
        uint256 reserveInWeth = getReserveInWeth(
            arithmeticMeanTickMarket,
            harmonicMeanLiquidityMarket
        );
        uint256 amountOfWethPerOvl = getQuoteAtTick(arithmeticMeanTickOvlWeth, ONE, ovl, WETH);
        reserveInOvl_ = FullMath.mulDiv(reserveInWeth, uint256(ONE), amountOfWethPerOvl);
    }

    /// @dev returns the virtual balance of WETH in the pool in OVL terms
    function getReserveInWeth(
        int24 arithmeticMeanTickMarket,
        uint128 harmonicMeanLiquidityMarket
    ) public view returns (uint256 reserveInWeth_) {
        // TODO: test this extensively
        uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick(arithmeticMeanTickMarket);
        reserveInWeth_ = marketToken0 == WETH
            ? FullMath.mulDiv(1 << 96, uint256(harmonicMeanLiquidityMarket), uint256(sqrtPriceX96)) // x (token0)
            : FullMath.mulDiv(uint256(harmonicMeanLiquidityMarket), uint256(sqrtPriceX96), 1 << 96); // y (token1)
    }

}
