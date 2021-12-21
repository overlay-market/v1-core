// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.10;

import "@uniswapv3/contracts/interfaces/IUniswapV3Pool.sol";

import "../OverlayFeed.sol";

contract UniswapV3OverlayFeed is OverlayFeed {
    address constant public WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    address immutable public marketPool;
    address immutable public ovlWethPool;

    address immutable public marketToken0;
    address immutable public marketToken1;
    address immutable public ovlWethToken0;
    address immutable public ovlWethToken1;

    constructor(
        address _marketPool,
        address _ovlWethPool,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayFeed(_microWindow, _macroWindow) {
        // need WETH in market pool to make reserve conversion from ETH => OVL
        address _marketToken0 = IUniswapV3Pool(_marketPool).token0();
        address _marketToken1 = IUniswapV3Pool(_marketPool).token1();

        require(_marketToken0 == WETH || _marketToken1 == WETH, "OVLV1Feed: marketToken != WETH");
        marketToken0 = _marketToken0;
        marketToken1 = _marketToken1;

        address _ovlWethToken0 = IUniswapV3Pool(_ovlWethPool).token0();
        address _ovlWethToken1 = IUniswapV3Pool(_ovlWethPool).token1();

        require(_ovlWethToken0 == WETH || _ovlWethToken1 == WETH, "OVLV1Feed: ovlWethToken != WETH");
        ovlWethToken0 = _ovlWethToken0;
        ovlWethToken1 = _ovlWethToken1;

        marketPool = _marketPool;
        ovlWethPool = _ovlWethPool;
    }

    /// @dev fetches TWAP, liquidity data from the univ3 pool oracle
    /// for micro and macro window averaging intervals
    function _fetch() internal virtual override returns (Oracle.Data memory) {
        (int24[2] memory arithmeticMeanTicksMarket, uint128[2] memory harmonicMeanLiquiditiesMarket) =
            _consult(marketPool);
        (int24[2] memory arithmeticMeanTicksOvlWeth, uint128[2] memory harmonicMeanLiquiditiesOvlWeth) =
            _consult(ovlWethPool);
    }

    function _consult(address pool) private returns (
        int24[2] memory arithmeticMeanTicks_,
        uint128[2] memory harmonicMeanLiquidities_
    ) {
        // COPIED AND MODIFIED FROM: Uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol
        uint32[] memory secondsAgos = new uint32[](3);
        secondsAgos[0] = uint32(macroWindow);
        secondsAgos[1] = uint32(microWindow);
        secondsAgos[2] = 0;

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
}
