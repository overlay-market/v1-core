// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "../IOverlayV1FeedFactory.sol";

interface IOverlayV1UniswapV3FeedFactory is IOverlayV1FeedFactory {
    // immutables
    function ovl() external view returns (address);

    function uniV3Factory() external view returns (address);

    // @dev required minimum observationCardinality for market and ovlX pools
    // TODO: function minCardinality() external view returns (uint16);

    // registry of feeds; for a given (pool, base, quote, amount) pair, returns associated feed
    function getFeed(
        address marketPool,
        address marketBaseToken,
        uint128 marketBaseAmount,
        address ovlXPool
    ) external view returns (address feed_);

    /// @dev deploys a new feed contract
    /// @return feed_ address of the new feed
    function deployFeed(
        address marketBaseToken,
        address marketQuoteToken,
        uint24 marketFee,
        uint128 marketBaseAmount,
        address ovlXBaseToken,
        address ovlXQuoteToken,
        uint24 ovlXFee
    ) external returns (address feed_);
}
