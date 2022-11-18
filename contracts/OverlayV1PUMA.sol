// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

import "./libraries/uniswap/v3-core/BitMath.sol";
import "./libraries/uniswap/v3-core/FullMath.sol";
import "./libraries/uniswap/v3-core/RemoteTickBitmap.sol";
import "./libraries/uniswap/v3-core/TickMath.sol";
import "./libraries/FixedPoint.sol";

import "./OverlayV1Token.sol";

import "forge-std/console.sol";
import "forge-std/console2.sol";


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

  function nextTick () public view returns (int24) {

    ( ,int24 current,,,,, ) = spot.slot0();

    int24 spacing = spot.tickSpacing();

    ( int24 next, bool init ) = RemoteTickBitmap.nextInitializedTickWithinOneWord(
      spot.tickBitmap,
      current,
      spacing,
      false
    );

    uint256 pricecurrent = getQuoteAtTick(
      current,
      1e18,
      address(ovl),
      address(x)
    );

    int24 tickreverse = getTickAtQuote(
      pricecurrent,
      1e18,
      address(ovl),
      address(x)
    );

    console.logInt(tickreverse);

    return next;

  }

  function current0 () public view returns (uint256) {

    ( ,int24 current,,,,, ) = spot.slot0();

    address t0 = spot.token0();
    address t1 = spot.token1();

    return getQuoteAtTick(
      current,
      1e18,
      t0,
      t1
    );

  }

  function current1 () public view returns (uint256) {

    ( ,int24 current,,,,, ) = spot.slot0();

    address t0 = spot.token0();
    address t1 = spot.token1();

    return getQuoteAtTick(
      current,
      1e18,
      t1,
      t0
    );

  }

  struct Slot0 {
      uint160 sqrtPriceX96;
      int24 tick;
      uint16 observationIndex;
      uint16 observationCardinality;
      uint16 observationCardinalityNext;
      uint8 feeProtocol;
      bool unlocked;
  }

  function slotZero () public view returns (Slot0 memory) {

    ( uint160 sqrtPrice,
      int24 tick,
      uint16 observationIndex,
      uint16 observationCardinality,
      uint16 observationCardinalityNext,
      uint8 feeProtocol,
      bool unlocked ) = spot.slot0();

      return Slot0(
        sqrtPrice,
        tick,
        observationIndex,
        observationCardinality,
        observationCardinalityNext,
        feeProtocol,
        unlocked
      );

  }

  function amountToMovePrice (uint priceDestination) public view {

    Slot0 memory slot0 = slotZero();


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

  function getTickAtQuote(
      uint256 quoteAmount,
      uint128 quoteUnitAmount,
      address baseToken,
      address quoteToken
  ) public view returns (int24 tick_) {

      uint256 baseAmount = FullMath.mulDiv(1e18, 1e18, quoteAmount);

      // TODO: know if it overflows and adjust accordingly
      uint256 ratio = baseToken < quoteToken
        ? FullMath.mulDiv(quoteAmount, 1 << 192, 1e18)
        : FullMath.mulDiv(quoteAmount, 1e18, 1 >> 192);

      uint256 root = sqrt(ratio);

      tick_ = TickMath.getTickAtSqrtRatio(uint160(root));

      console.log(root);

  }

  function sqrt(uint input) internal pure returns (uint output) {

      if (input > 3) {

          output = input;
          uint intermediate = input / 2 + 1;
          while (intermediate < output) {
              output = intermediate;
              intermediate = (input / intermediate + intermediate) / 2;
          }

      } else if (input != 0) {

          output = 1;

      }

  }

}
