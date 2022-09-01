// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

// forks of uniswap libraries for solidity^0.8.10
import "../../libraries/uniswap/v3-core/FullMath.sol";
import "../../libraries/uniswap/v3-core/TickMath.sol";

import "../OverlayV1Feed.sol";

contract OverlayV1UniswapV3InverseFeed is OverlayV1Feed {
    uint128 internal constant ONE = 1e18; // 18 decimal places for ovl

    // relevant pools for the feed
    // no market pool as we will use ethXPool to get price
    address public immutable ethXPool;
    address public immutable ovlEthPool;

    // market tokens
    address public immutable marketToken0; // X or OVL
    address public immutable marketToken1; // X or OVL

    // ethXPool tokens
    address public immutable xPoolToken0;
    address public immutable xPoolToken1;

    // marketPool base and quote token arrangements
    address public immutable marketBaseToken; // X
    address public immutable marketQuoteToken; // OVL
    uint128 public immutable marketBaseAmount; // unit of x

    // ovlEthPool tokens
    // @dev weth is the common token between ethXPool and ovlEthPool
    address public immutable ovl;
    address public immutable weth;

    constructor(
        address _ethXPool,
        address _marketBaseToken,
        uint128 _marketBaseAmount,
        address _ovlEthPool,
        address _ovl,
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _cardinalityMinimum
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        // determine X token
        // need OVL/X pool for ovl vs X price to make reserve conversion from X => OVL
        address _ovlXToken0 = IUniswapV3Pool(_ovlEthPool).token0();
        address _ovlXToken1 = IUniswapV3Pool(_ovlEthPool).token1();
        require(_ovlXToken0 == _ovl || _ovlXToken1 == _ovl, "OVLV1: ovlXToken != OVL");
        weth = _ovlXToken0 == _ovl ? _ovlXToken1 : _ovlXToken0;

        // need X in market pool to make reserve conversion from X => OVL
        address _marketToken0 = IUniswapV3Pool(_ethXPool).token0();
        address _marketToken1 = IUniswapV3Pool(_ethXPool).token1();

        require(_marketToken0 == weth || _marketToken1 == weth, "OVLV1: marketToken != X");
        marketToken0 = _ovl;
        marketToken1 = _marketToken0 == weth ? _marketToken1 : _marketToken0;

        xPoolToken0 = _marketToken0;
        xPoolToken1 = _marketToken1;

        require(
            _marketToken0 == _marketBaseToken || _marketToken1 == _marketBaseToken,
            "OVLV1: marketToken != marketBaseToken"
        );

        marketBaseToken = _marketBaseToken;
        marketQuoteToken = _ovl;
        marketBaseAmount = _marketBaseAmount;

        // check observation cardinality large enough for market and
        // ovl pool on deploy
        (, , , uint16 observationCardinalityOvlX, , , ) = IUniswapV3Pool(_ovlEthPool).slot0();
        require(
            observationCardinalityOvlX >= _cardinalityMinimum,
            "OVLV1: ovlXCardinality < min"
        );

        (, , , uint16 observationCardinalityMarket, , , ) = IUniswapV3Pool(_ethXPool).slot0();
        require(
            observationCardinalityMarket >= _cardinalityMinimum,
            "OVLV1: marketCardinality < min"
        );

        ethXPool = _ethXPool;
        ovlEthPool = _ovlEthPool;
        ovl = _ovl;
    }


    /// @dev fetches TWAP, liquidity data from the univ3 pool oracle
    /// @dev for micro and macro window averaging intervals.
    /// @dev market pool and ovlX pool have different consult inputs
    /// @dev to minimize accumulator snapshot queries with consult
    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // consult to market pool
        // secondsAgo.length = 4; twaps.length = liqs.length = 3
        address _quoteToken = ethXPool == ovlEthPool ? ovl : weth;
        (
            uint32[] memory secondsAgos,
            uint32[] memory windows,
            uint256[] memory nowIdxs
        ) = _inputsToConsultMarketPool(microWindow, macroWindow);
        (
            int24[] memory arithmeticMeanTicksMarket,
            uint128[] memory harmonicMeanLiquiditiesMarket
        ) = consult(ethXPool, secondsAgos, windows, nowIdxs);


        // in terms of prices, will use for indexes
        //  0: priceOneMacroWindowAgo: prices[0]
        //  1: priceOverMacroWindow: prices[1]
        //  2: priceOverMicroWindow: prices[2]
        // window: [now - macroWindow * 2, now - macroWindow]
        uint256 priceOneMacroWindowAgo = getQuoteAtTick(
            arithmeticMeanTicksMarket[0],
            marketBaseAmount,
            marketBaseToken,
            weth
        );
        // window: [now - macroWindow, now]
        uint256 priceOverMacroWindow = getQuoteAtTick(
            arithmeticMeanTicksMarket[1],
            marketBaseAmount,
            marketBaseToken,
            weth
        );
        // window: [now - microWindow, now]
        uint256 priceOverMicroWindow = getQuoteAtTick(
            arithmeticMeanTicksMarket[2],
            marketBaseAmount,
            marketBaseToken,
            weth
        );

        // reserve calculation done over window: [now - microWindow, now]
        // needs ovlX price over micro to convert into OVL terms from X
        // get mean ticks of X in OVL to convert reserveInX to reserveInOvl
        int24 arithmeticMeanTickOvlX;
        if (ethXPool == ovlEthPool) {
            // simply mean ticks over the micro window of market pool
            // NOTE: saves the additional consult call to ovlXPool
            arithmeticMeanTickOvlX = arithmeticMeanTicksMarket[2];
        } else {
            // // consult to ovlX pool
            // // secondsAgo.length = 2; twaps.length = liqs.length = 1
            // (
            //     uint32[] memory secondsAgosOvlX,
            //     uint32[] memory windowsOvlX,
            //     uint256[] memory nowIdxsOvlX
            // ) = _inputsToConsultOvlXPool(microWindow, macroWindow);
            (int24[] memory arithmeticMeanTicksOvlX, ) = consult(
                ovlEthPool,
                secondsAgos, 
                windows, 
                nowIdxs
            );

            arithmeticMeanTickOvlX = arithmeticMeanTicksOvlX[2];        


            priceOneMacroWindowAgo = FullMath.mulDiv(priceOneMacroWindowAgo, getQuoteAtTick(
                                    arithmeticMeanTicksOvlX[0], 
                                    ONE, 
                                    weth, 
                                    ovl), ONE);

            priceOverMacroWindow = FullMath.mulDiv(priceOverMacroWindow, getQuoteAtTick(
                                    arithmeticMeanTicksOvlX[1], 
                                    ONE, 
                                    weth, 
                                    ovl), ONE);

            priceOverMicroWindow = FullMath.mulDiv(priceOverMicroWindow, getQuoteAtTick(
                                    arithmeticMeanTicksOvlX[2], 
                                    ONE, 
                                    weth, 
                                    ovl), ONE);
        }

        // reserve is the reserve in marketPool over micro window
        // window: [now - microWindow, now]
        uint256 reserve = getReserveInOvl(
            arithmeticMeanTicksMarket[2],
            harmonicMeanLiquiditiesMarket[2],
            arithmeticMeanTickOvlX
        );


        return
            Oracle.Data({
                timestamp: block.timestamp,
                microWindow: microWindow,
                macroWindow: macroWindow,
                priceOverMicroWindow: priceOverMicroWindow,
                priceOverMacroWindow: priceOverMacroWindow,
                priceOneMacroWindowAgo: priceOneMacroWindowAgo,
                reserveOverMicroWindow: reserve,
                hasReserve: true
            });
    }

    /// @dev returns input params needed for call to marketPool consult
    function _inputsToConsultMarketPool(uint256 _microWindow, uint256 _macroWindow)
        private
        pure
        returns (
            uint32[] memory,
            uint32[] memory,
            uint256[] memory
        )
    {
        uint32[] memory secondsAgos = new uint32[](4);
        uint32[] memory windows = new uint32[](3);
        uint256[] memory nowIdxs = new uint256[](3);

        // number of seconds in past for which we want accumulator snapshot
        // for Oracle.Data, need:
        //  0: now - 2 * macroWindow (2 * macroWindow seconds ago)
        //  1: now - macroWindow (macroWindow seconds ago)
        //  2: now - microWindow (microWindow seconds ago)
        //  3: now (0 seconds ago)
        secondsAgos[0] = uint32(_macroWindow * 2);
        secondsAgos[1] = uint32(_macroWindow);
        secondsAgos[2] = uint32(_microWindow);
        secondsAgos[3] = 0;

        // window lengths for each cumulative differencing
        // in terms of prices, will use for indexes
        //  0: priceOneMacroWindowAgo
        //  1: priceOverMacroWindow
        //  2: priceOverMicroWindow
        windows[0] = uint32(_macroWindow);
        windows[1] = uint32(_macroWindow);
        windows[2] = uint32(_microWindow);

        // index of secondsAgos which we treat as current time when differencing
        // for mean calcs
        //  0: priceOneMacroWindowAgo
        //  1: priceOverMacroWindow
        //  2: priceOverMicroWindow
        nowIdxs[0] = 1;
        nowIdxs[1] = 3;
        nowIdxs[2] = 3;

        return (secondsAgos, windows, nowIdxs);
    }

    /// @dev COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
    /// @dev assumes nows elements are the current cumulative value from which we
    /// @dev want to calculate rolling average tick and liquidity values
    function consult(
        address pool,
        uint32[] memory secondsAgos,
        uint32[] memory windows,
        uint256[] memory nowIdxs
    )
        public
        view
        returns (int24[] memory arithmeticMeanTicks_, uint128[] memory harmonicMeanLiquidities_)
    {
        (
            int56[] memory tickCumulatives,
            uint160[] memory secondsPerLiquidityCumulativeX128s
        ) = IUniswapV3Pool(pool).observe(secondsAgos);

        uint256 nowIdxsLength = nowIdxs.length;
        arithmeticMeanTicks_ = new int24[](nowIdxsLength);
        harmonicMeanLiquidities_ = new uint128[](nowIdxsLength);

        for (uint256 i = 0; i < nowIdxsLength; i++) {
            uint256 nowIdx = nowIdxs[i];
            uint32 window = windows[i];

            int56 tickCumulativesDelta = tickCumulatives[nowIdx] - tickCumulatives[i];
            uint160 secondsPerLiquidityCumulativesDelta = secondsPerLiquidityCumulativeX128s[
                nowIdx
            ] - secondsPerLiquidityCumulativeX128s[i];

            int24 arithmeticMeanTick = int24(tickCumulativesDelta / int56(uint56(window)));
            // Always round to negative infinity
            if (tickCumulativesDelta < 0 && (tickCumulativesDelta % int56(uint56(window)) != 0))
                arithmeticMeanTick--;

            unchecked {
                // We are multiplying here instead of shifting to ensure that harmonicMeanLiquidity
                // doesn't overflow uint128
                uint192 windowX160 = uint192(window) * type(uint160).max;
                uint128 harmonicMeanLiquidity = uint128(
                    windowX160 / (uint192(secondsPerLiquidityCumulativesDelta) << 32)
                );

                arithmeticMeanTicks_[i] = arithmeticMeanTick;
                harmonicMeanLiquidities_[i] = harmonicMeanLiquidity;
            }
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

        // Calculate quoteAmount with better precision if it doesn't overflow when multiplied by
        // itself
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

    /// @dev virtual balance of X in the pool in OVL terms
    function getReserveInOvl(
        int24 arithmeticMeanTickMarket,
        uint128 harmonicMeanLiquidityMarket,
        int24 arithmeticMeanTickOvlX
    ) public view returns (uint256 reserveInOvl_) {
        uint256 reserveInWeth = getReserveInWeth(arithmeticMeanTickMarket, harmonicMeanLiquidityMarket);
        uint256 amountOfWethPerOvl = getQuoteAtTick(arithmeticMeanTickOvlX, ONE, ovl, weth);
        reserveInOvl_ = FullMath.mulDiv(reserveInWeth, uint256(ONE), amountOfWethPerOvl);
    }

    /// @dev virtual balance of X in the pool
    function getReserveInWeth(int24 arithmeticMeanTickMarket, uint128 harmonicMeanLiquidityMarket)
        public
        view
        returns (uint256 reserveInX_)
    {
        uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick(arithmeticMeanTickMarket);
        // X ? x (token0) : y (token1)
        reserveInX_ = xPoolToken0 == weth
            ? FullMath.mulDiv(1 << 96, uint256(harmonicMeanLiquidityMarket), uint256(sqrtPriceX96))
            : FullMath.mulDiv(
                uint256(harmonicMeanLiquidityMarket),
                uint256(sqrtPriceX96),
                1 << 96
            );
    }    


}
