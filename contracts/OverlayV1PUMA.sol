// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

import "./libraries/uniswap/v3-core/FullMath.sol";
import "./libraries/uniswap/v3-core/TickMath.sol";

import "./OverlayV1Token.sol";

contract OverlayV1PUMA {

  IERC20 immutable x;
  OverlayV1Token immutable ovl;
  IUniswapV3Pool immutable spot;

  constructor (
    address _ovl,
    address _spot
  ) {

    address _spot0 = IUniswapV3Pool(_spot).token0();
    address _spot1 = IUniswapV3Pool(_spot).token1();

    x = _spot0 == _ovl ? IERC20(_spot1) : IERC20(_spot0);
    ovl = OverlayV1Token(_ovl);
    spot = IUniswapV3Pool(_spot);

  }

  // Compute all unrealized positions.

  function detect (
    uint256 window
  ) public view {

    uint32[] memory thepast = new uint32[](3);
    thepast[0] = 0;
    thepast[1] = 1;
    thepast[2] = uint32(window);

    ( int56[] memory ticks, uint160[] memory liqs ) = spot.observe(thepast);

    int24 nowtick = int24(ticks[0] - ticks[1]);

    uint256 pricenow = getQuoteAtTick(
      nowtick,
      1e18,
      address(ovl),
      address(x)
    );

    int24 thentick = int24((ticks[0] - ticks[2]) / int56(uint56(window)));

    uint256 pricethen = getQuoteAtTick(
      thentick,
      1e18,
      address(ovl),
      address(x)
    );

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
