// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../IOverlayV1FeedFactory.sol";

interface IOverlayV1NFTPerpFeedFactory is IOverlayV1FeedFactory {
    // registry of feeds; for a given aggregator, returns associated feed
    function getFeed(address _aggregator) external view returns (address _feed);

    /// @dev deploys a new feed contract
    /// @return _feed address of the new feed
    function deployFeed(address _aggregator, uint8 _decimal) external returns (address _feed);
}
