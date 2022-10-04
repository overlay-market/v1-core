// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

// forks of uniswap libraries for solidity^0.8.10
import "../../libraries/uniswap/v3-core/FullMath.sol";
import "../../libraries/uniswap/v3-core/TickMath.sol";

import "../OverlayV1Feed.sol";

contract OverlayV1UniswapV3MultiplexFeed is OverlayV1Feed {
    uint128 internal constant ONE = 1e18; // 18 decimal places for ovl

    // relevant pools for the feed
    // no market pool as we will use baseXPool and xQuotePool to get price
    address public immutable basePool;
    address public immutable quotePool;

    // basePool tokens
    address public immutable basePoolToken0;
    address public immutable basePoolToken1;

    // quotePool tokens
    address public immutable quotePoolToken0;
    address public immutable quotePoolToken1;


    // marketPool base and quote token arrangements
    address public immutable marketBaseToken; // X
    address public immutable marketQuoteToken; // OVL
    uint128 public immutable marketBaseAmount; // unit of x

    // ovlEthPool tokens
    // @dev x is the common token between basePool and quotePool
    address public immutable x;

    constructor(
        address _basePool,
        address _marketBaseToken,
        uint128 _marketBaseAmount,
        address _marketQuoteToken,
        address _quotePool,
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _cardinalityMinimum
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        // determine X token
        // need OVL/X pool for ovl vs X price to make reserve conversion from X => OVL

        require(_basePool != _quotePool, "OVLV1: Same pool");

        address _baseToken0 = IUniswapV3Pool(_basePool).token0();
        address _baseToken1 = IUniswapV3Pool(_basePool).token1();
        require(_baseToken0 == _marketBaseToken || _baseToken1 == _marketBaseToken, "OVLV1: basePoolToken != base token");

        x = _baseToken0 == _marketBaseToken ? _baseToken1 : _baseToken0;

        // need X in market pool to make reserve conversion from X => OVL
        address _quoteToken0 = IUniswapV3Pool(_quotePool).token0();
        address _quoteToken1 = IUniswapV3Pool(_quotePool).token1();

        require(_quoteToken0 == _marketQuoteToken || _quoteToken1 == _marketQuoteToken, "OVLV1: quotePoolToken != quote token");
        
        require(_quoteToken0 == x || _quoteToken1 == x, "OVLV1: quotePoolToken != x");
        
        basePoolToken0 = _baseToken0;
        basePoolToken1 = x;

        quotePoolToken0 = _quoteToken0;
        quotePoolToken1 = _quoteToken1;


        marketBaseToken = _marketBaseToken;
        marketQuoteToken = _marketQuoteToken;
        marketBaseAmount = _marketBaseAmount;

        // check observation cardinality large enough for market and
        // ovl pool on deploy
        (, , , uint16 observationCardinalityOvlX, , , ) = IUniswapV3Pool(_basePool).slot0();
        require(
            observationCardinalityOvlX >= _cardinalityMinimum,
            "OVLV1: basePoolCardinality < min"
        );

        (, , , uint16 observationCardinalityMarket, , , ) = IUniswapV3Pool(_quotePool).slot0();
        require(
            observationCardinalityMarket >= _cardinalityMinimum,
            "OVLV1: quotePoolCardinality < min"
        );

        basePool = _basePool;
        quotePool = _quotePool;
    }


    /// @dev fetches TWAP, liquidity data from the univ3 pool oracle
    /// @dev for micro and macro window averaging intervals.
    /// @dev market pool and ovlX pool have different consult inputs
    /// @dev to minimize accumulator snapshot queries with consult
    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // consult to market pool
        // secondsAgo.length = 4; twaps.length = liqs.length = 3
        (
            uint32[] memory secondsAgos,
            uint32[] memory windows,
            uint256[] memory nowIdxs
        ) = _inputsToConsultMarketPool(microWindow, macroWindow);
        (
            int24[] memory arithmeticMeanTicksMarket,
            uint128[] memory harmonicMeanLiquiditiesMarket
        ) = consult(basePool, secondsAgos, windows, nowIdxs);


        // in terms of prices, will use for indexes
        //  0: priceOneMacroWindowAgo: prices[0]
        //  1: priceOverMacroWindow: prices[1]
        //  2: priceOverMicroWindow: prices[2]
        // window: [now - macroWindow * 2, now - macroWindow]
        uint256 priceOneMacroWindowAgo = getQuoteAtTick(
            arithmeticMeanTicksMarket[0],
            marketBaseAmount,
            marketBaseToken,
            x
        );
        // window: [now - macroWindow, now]
        uint256 priceOverMacroWindow = getQuoteAtTick(
            arithmeticMeanTicksMarket[1],
            marketBaseAmount,
            marketBaseToken,
            x
        );
        // window: [now - microWindow, now]
        uint256 priceOverMicroWindow = getQuoteAtTick(
            arithmeticMeanTicksMarket[2],
            marketBaseAmount,
            marketBaseToken,
            x
        );

        // reserve calculation done over window: [now - microWindow, now]
        // needs xQuote price over micro to convert into quote terms from X

        // // consult to xQuote pool
        // // secondsAgo.length = 2; twaps.length = liqs.length = 1
        (int24[] memory arithmeticMeanTicksQuote, ) = consult(
            quotePool,
            secondsAgos, 
            windows, 
            nowIdxs
        );


        priceOneMacroWindowAgo = getQuoteAtTick(
                                arithmeticMeanTicksQuote[0], 
                                uint128(priceOneMacroWindowAgo), 
                                x, 
                                marketQuoteToken);

        priceOverMacroWindow = getQuoteAtTick(
                                arithmeticMeanTicksQuote[1], 
                                uint128(priceOverMacroWindow), 
                                x, 
                                marketQuoteToken);

        priceOverMicroWindow = getQuoteAtTick(
                                arithmeticMeanTicksQuote[2], 
                                uint128(priceOverMicroWindow), 
                                x, 
                                marketQuoteToken);

        ////// X/Y pool Y/Z pool, X = 2e18 Y(18 decimal), Y = 5e6 Z(6 decimal), X = 10e24 / Y decimals Z (6 decimal)
        ////// X/Y pool Y/Z pool, X = 2e6 Y(6 decimal), Y = 5e18 Z(18 decimal), X = 10e24 / Y decimals Z (18 decimal)

        return
            Oracle.Data({
                timestamp: block.timestamp,
                microWindow: microWindow,
                macroWindow: macroWindow,
                priceOverMicroWindow: priceOverMicroWindow,
                priceOverMacroWindow: priceOverMacroWindow,
                priceOneMacroWindowAgo: priceOneMacroWindowAgo,
                reserveOverMicroWindow: 0,
                hasReserve: false
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


    /// @dev virtual balance of X in the pool
    function getReserveInQuote(int24 arithmeticMeanTickMarket, uint128 harmonicMeanLiquidityMarket)
        public
        view
        returns (uint256 reserveInX_)
    {
        uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick(arithmeticMeanTickMarket);
        // X ? x (token0) : y (token1)
        reserveInX_ = quotePoolToken0 == marketQuoteToken
            ? FullMath.mulDiv(1 << 96, uint256(harmonicMeanLiquidityMarket), uint256(sqrtPriceX96))
            : FullMath.mulDiv(
                uint256(harmonicMeanLiquidityMarket),
                uint256(sqrtPriceX96),
                1 << 96
            );
    }    


}
