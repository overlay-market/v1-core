// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../OverlayV1FeedFactory.sol";
import "./OverlayV1ChainlinkFeedRatio.sol";

contract OverlayV1ChainlinkFeedRatioFactory is OverlayV1FeedFactory {
    address public immutable ovl;
    // registry of feeds; for a given aggregator pair, returns associated feed
    mapping(address => mapping(address => address)) public aggregatorPairToFeed;


    constructor(address _ovl, uint256 _microWindow, uint256 _macroWindow)
        OverlayV1FeedFactory(_microWindow, _macroWindow)
    {
        require(_ovl != address(0), "OVLV1: invalid ovl");
        ovl = _ovl;
    }

    function getFeed(address _base, address _quote) external view returns (address) {
        return aggregatorPairToFeed[_base][_quote];
    }

    /// @dev deploys a new ratio feed contract
    /// @param _baseAggregator base chainlink price feed
    /// @param _quoteAggregator quote chainlink price feed
    /// @param _heartbeat expected update frequency of the feed
    /// @return _feed address of the new feed
    function deployFeed(
        address _baseAggregator,
        address _quoteAggregator,
        uint256 _heartbeat
    )
        external
        returns (address _feed)
    {
        // check feed doesn't already exist
        require(aggregatorPairToFeed[_baseAggregator][_quoteAggregator] == address(0), "OVLV1: feed already exists");

        // Create a new Feed contract
        _feed = address(
            new OverlayV1ChainlinkFeedRatio(
                ovl,
                _baseAggregator,
                _quoteAggregator,
                microWindow,
                macroWindow,
                _heartbeat
            )
        );

        // store feed registry record for aggregator pair and record address as deployed feed
        aggregatorPairToFeed[_baseAggregator][_quoteAggregator] = _feed;
        isFeed[_feed] = true;

        emit FeedDeployed(msg.sender, _feed);
    }
}
