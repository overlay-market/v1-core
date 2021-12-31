// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

interface IOverlayV1UniswapV3Feed {
    function marketPool() external view returns (address);
    function ovlWethPool() external view returns (address);
    function ovl() external view returns (address);
    function marketBaseToken() external view returns (address);
    function marketQuoteToken() external view returns (address);
    function marketBaseAmount() external view returns (uint128);
}
