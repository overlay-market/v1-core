// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../IOverlayV1FeedFactory.sol";

interface IOverlayV1NoReserveUniswapV3FeedFactory is IOverlayV1FeedFactory {
    function uniV3Factory() external view returns (address);

    // @dev minimum observationCardinality needed for micro and macro windows
    function observationCardinalityMinimum() external view returns (uint16);

    // registry of feeds; for a given (pool, base, quote, amount) pair, returns associated feed
    function getFeed(
        address marketPool,
        address marketBaseToken,
        uint128 marketBaseAmount
    ) external view returns (address feed_);

    /// @dev deploys a new feed contract
    /// @return feed_ address of the new feed
    function deployFeed(
        address marketBaseToken,
        address marketQuoteToken,
        uint24 marketFee,
        uint128 marketBaseAmount
    ) external returns (address feed_);
}
