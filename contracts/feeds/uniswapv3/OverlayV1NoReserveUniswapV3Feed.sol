// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

// forks of uniswap libraries for solidity^0.8.10
import "../../libraries/uniswap/v3-core/FullMath.sol";
import "../../libraries/uniswap/v3-core/TickMath.sol";

import "../../interfaces/feeds/uniswapv3/IOverlayV1NoReserveUniswapV3Feed.sol";
import "../OverlayV1Feed.sol";

contract OverlayV1NoReserveUniswapV3Feed is IOverlayV1NoReserveUniswapV3Feed, OverlayV1Feed {
    // relevant pools for the feed
    address public immutable marketPool;

    // marketPool tokens
    address public immutable marketToken0;
    address public immutable marketToken1;

    // marketPool base and quote token arrangements
    address public immutable marketBaseToken;
    address public immutable marketQuoteToken;
    uint128 public immutable marketBaseAmount;

    constructor(
        address _marketPool,
        address _marketBaseToken,
        address _marketQuoteToken,
        uint128 _marketBaseAmount,
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _cardinalityMarketMinimum
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        address _marketToken0 = IUniswapV3Pool(_marketPool).token0();
        address _marketToken1 = IUniswapV3Pool(_marketPool).token1();

        require(
            _marketToken0 == _marketBaseToken || _marketToken1 == _marketBaseToken,
            "OVLV1: marketToken != marketBaseToken"
        );
        require(
            _marketToken0 == _marketQuoteToken || _marketToken1 == _marketQuoteToken,
            "OVLV1: marketToken != marketQuoteToken"
        );

        marketToken0 = _marketToken0;
        marketToken1 = _marketToken1;

        marketBaseToken = _marketBaseToken;
        marketQuoteToken = _marketQuoteToken;
        marketBaseAmount = _marketBaseAmount;

        (, , , uint16 observationCardinalityMarket, , , ) = IUniswapV3Pool(_marketPool).slot0();
        require(
            observationCardinalityMarket >= _cardinalityMarketMinimum,
            "OVLV1: marketCardinality < min"
        );

        marketPool = _marketPool;
    }

    /// @dev fetches TWAP, liquidity data from the univ3 pool oracle
    /// @dev for micro and macro window averaging intervals.
    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // consult to market pool
        // secondsAgo.length = 4; twaps.length = liqs.length = 3
        (
            uint32[] memory secondsAgos,
            uint32[] memory windows,
            uint256[] memory nowIdxs
        ) = _inputsToConsultMarketPool(microWindow, macroWindow);

        int24[] memory arithmeticMeanTicksMarket = consult(
            marketPool,
            secondsAgos,
            windows,
            nowIdxs
        );

        // in terms of prices, will use for indexes
        //  0: priceOneMacroWindowAgo: prices[0]
        //  1: priceOverMacroWindow: prices[1]
        //  2: priceOverMicroWindow: prices[2]
        // window: [now - macroWindow * 2, now - macroWindow]
        uint256 priceOneMacroWindowAgo = getQuoteAtTick(
            arithmeticMeanTicksMarket[0],
            marketBaseAmount,
            marketBaseToken,
            marketQuoteToken
        );
        // window: [now - macroWindow, now]
        uint256 priceOverMacroWindow = getQuoteAtTick(
            arithmeticMeanTicksMarket[1],
            marketBaseAmount,
            marketBaseToken,
            marketQuoteToken
        );
        // window: [now - microWindow, now]
        uint256 priceOverMicroWindow = getQuoteAtTick(
            arithmeticMeanTicksMarket[2],
            marketBaseAmount,
            marketBaseToken,
            marketQuoteToken
        );

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
    ) public view returns (int24[] memory arithmeticMeanTicks_) {
        (
            int56[] memory tickCumulatives,
            uint160[] memory secondsPerLiquidityCumulativeX128s
        ) = IUniswapV3Pool(pool).observe(secondsAgos);

        uint256 nowIdxsLength = nowIdxs.length;
        arithmeticMeanTicks_ = new int24[](nowIdxsLength);

        for (uint256 i = 0; i < nowIdxsLength; i++) {
            uint256 nowIdx = nowIdxs[i];
            uint32 window = windows[i];

            int56 tickCumulativesDelta = tickCumulatives[nowIdx] - tickCumulatives[i];

            int24 arithmeticMeanTick = int24(tickCumulativesDelta / int56(uint56(window)));
            // Always round to negative infinity
            if (tickCumulativesDelta < 0 && (tickCumulativesDelta % int56(uint56(window)) != 0))
                arithmeticMeanTick--;

            arithmeticMeanTicks_[i] = arithmeticMeanTick;
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
}
