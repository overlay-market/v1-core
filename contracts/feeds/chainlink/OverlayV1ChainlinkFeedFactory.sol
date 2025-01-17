// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../OverlayV1FeedFactory.sol";
import "./OverlayV1ChainlinkFeed.sol";
import "../../interfaces/feeds/chainlink/IOverlayV1ChainlinkFeedFactory.sol";

contract OverlayV1ChainlinkFeedFactory is IOverlayV1ChainlinkFeedFactory, OverlayV1FeedFactory {
    address public immutable ovl;
    // registry of feeds; for a given aggregator pair, returns associated feed
    mapping(address => address) public getFeed;

    constructor(address _ovl, uint256 _microWindow, uint256 _macroWindow)
        OverlayV1FeedFactory(_microWindow, _macroWindow)
    {
        require(_ovl != address(0), "OVLV1: invalid ovl");
        ovl = _ovl;
    }

    /// @dev deploys a new feed contract
    /// @param _aggregator chainlink price feed
    /// @param _heartbeat expected update frequency of the feed
    /// @return _feed address of the new feed
    function deployFeed(address _aggregator, uint256 _heartbeat)
        external
        returns (address _feed)
    {
        // check feed doesn't already exist
        require(getFeed[_aggregator] == address(0), "OVLV1: feed already exists");

        // Create a new Feed contract
        _feed = address(
            new OverlayV1ChainlinkFeed(ovl, _aggregator, microWindow, macroWindow, _heartbeat)
        );

        // store feed registry record for _aggregator and record address as deployed feed
        getFeed[_aggregator] = _feed;
        isFeed[_feed] = true;

        emit FeedDeployed(msg.sender, _feed);
    }
}
