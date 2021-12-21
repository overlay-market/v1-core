// SPDX-License-Identifier: MIT
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

    }
}
