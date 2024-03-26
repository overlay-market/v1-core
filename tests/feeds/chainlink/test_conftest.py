def test_chainlink_feed_fixture(chainlink_feed, mock_aggregator):
    assert chainlink_feed.microWindow() == 600
    assert chainlink_feed.macroWindow() == 3600
    assert chainlink_feed.aggregator() == mock_aggregator.address
