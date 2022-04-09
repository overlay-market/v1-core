// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

// SN TODO: Direct copy from IOverlayV1UniswapV3Feed.sol -> Needs modification to suit the
// OverlayV1BalancerV2Feed.sol contract
import "../IOverlayV1Feed.sol";

interface IOverlayV1BalancerV2Feed is IOverlayV1Feed {
    function marketPool() external view returns (address);

    function ovlWethPool() external view returns (address);

    function ovl() external view returns (address);

    function marketToken0() external view returns (address);

    function marketToken1() external view returns (address);

    function ovlWethToken0() external view returns (address);

    function ovlWethToken1() external view returns (address);

    function marketBaseToken() external view returns (address);

    function marketQuoteToken() external view returns (address);

    function marketBaseAmount() external view returns (uint128);

    function ovlWethPoolId() external view returns (bytes32);

    /// @notice Virtual balance of WETH in the pool
    function getReserveInWeth(uint256 twav, uint256 priceOverMicroWindow)
        external
        view
        returns (uint256 reserveInWeth_);
}
