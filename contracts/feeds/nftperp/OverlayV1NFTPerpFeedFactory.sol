// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../OverlayV1FeedFactory.sol";
import "./OverlayV1NFTPerpFeed.sol";
import "../../interfaces/feeds/nftperp/IOverlayV1NFTPerpFeedFactory.sol";

contract OverlayV1NFTPerpFeedFactory is IOverlayV1NFTPerpFeedFactory, OverlayV1FeedFactory {
    // registry of feeds; for a given aggregator pair, returns associated feed
    mapping(address => address) public getFeed;

    constructor(uint256 _microWindow, uint256 _macroWindow)
        OverlayV1FeedFactory(_microWindow, _macroWindow)
    {}

    /// @dev deploys a new feed contract
    /// @param _aggregator chainlink price feed
    /// @return _feed address of the new feed
    function deployFeed(address _aggregator, uint8 _decimal) external returns (address _feed) {
        // check feed doesn't already exist
        require(getFeed[_aggregator] == address(0), "OVLV1: feed already exists");

        // Create a new Feed contract
        _feed = address(new OverlayV1NFTPerpFeed(_aggregator, microWindow, macroWindow, _decimal));

        // store feed registry record for _aggregator and record address as deployed feed
        getFeed[_aggregator] = _feed;
        isFeed[_feed] = true;

        emit FeedDeployed(msg.sender, _feed);
    }
}
