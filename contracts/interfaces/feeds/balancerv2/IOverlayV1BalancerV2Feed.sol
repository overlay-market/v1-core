// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "../IOverlayV1Feed.sol";
import "./IBalancerV2PriceOracle.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

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

    /// @notice Returns the OracleAverageQuery struct containing information for a TWAP query
    function getOracleAverageQuery(
        IBalancerV2PriceOracle.Variable variable,
        uint256 secs,
        uint256 ago
    ) external view returns (IBalancerV2PriceOracle.OracleAverageQuery memory);

    /// @notice Returns the time average weighted price corresponding to each of queries.
    function getTimeWeightedAverage(
        address pool,
        IBalancerV2PriceOracle.OracleAverageQuery[] memory queries
    ) external view returns (uint256[] memory twaps_);

    /// @notice Returns the TWAP corresponding to a single query for the price of the tokens in the
    /// @notice pool, expressed as the price of the second token in units of the first token
    /// @dev SN TODO: NOT USED
    function getTimeWeightedAveragePairPrice(
        address pool,
        uint256 secs,
        uint256 ago
    ) external view returns (uint256 result);

    /// @notice Returns the TWAI (time weighted average invariant) corresponding to a single query
    /// @notice for the value of the pool's
    /// @notice invariant, which is a measure of its liquidity
    function getTimeWeightedAverageInvariant(
        address pool,
        uint256 secs,
        uint256 ago
    ) external view returns (uint256 result_);

    /// @notice Returns pool token information given a pool id
    function getPoolTokens(bytes32 balancerV2PoolId)
        external
        view
        returns (
            IERC20[] memory,
            uint256[] memory,
            uint256
        );

    /// @notice Returns the pool id corresponding to the given pool address
    function getPoolId(address pool) external view returns (bytes32 _poolId);

    /// @notice Returns the normalized weight of the token
    function getNormalizedWeights(address pool) external view returns (uint256[] memory weights_);

    function getReserve(uint256 priceOverMicroWindow) external view returns (uint256 reserve_);

    /// @notice Virtual balance of WETH in the pool
    function getReserveInWeth(uint256 twav, uint256 priceOverMicroWindow)
        external
        view
        returns (uint256 reserveInWeth_);

    /// @notice Market pool only (not reserve)
    function getPairPriceOvlWeth() external view returns (uint256 twap_);

    /// @notice Market pool only (not reserve)
    function getPairPrices() external view returns (uint256[] memory twaps_);
}
