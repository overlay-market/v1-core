from brownie import reverts, OverlayV1FeedMock
from collections import OrderedDict


def test_deploy_feed_creates_feed(factory, alice):
    price = 1000000000000000000
    reserve = 2000000000000000000

    tx = factory.deployFeed(price, reserve, {"from": alice})
    actual_feed = tx.return_value

    # check feed is added to registry
    assert factory.getFeed(price, reserve) == actual_feed
    assert factory.isFeed(actual_feed) is True

    # check event emitted
    assert 'FeedDeployed' in tx.events
    expect_event = OrderedDict({
        "user": alice.address,
        "feed": actual_feed
    })
    actual_event = tx.events['FeedDeployed']
    assert actual_event == expect_event

    # check feed deployed with correct immutables set
    feed_contract = OverlayV1FeedMock.at(actual_feed)
    assert feed_contract.microWindow() == 600
    assert feed_contract.macroWindow() == 3600
    assert feed_contract.feedFactory() == factory


def test_deploy_feed_reverts_when_feed_already_exists(factory, alice):
    price = 1000000000000000000
    reserve = 2000000000000000000

    # Check feed already exists first from prior unit test above
    feed = factory.getFeed(price, reserve)
    assert factory.isFeed(feed) is True

    # check reverts when attempt to deploy again
    with reverts("OVLV1: feed already exists"):
        _ = factory.deployFeed(price, reserve, {"from": alice})
