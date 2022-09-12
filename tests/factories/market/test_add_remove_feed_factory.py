from brownie import reverts
from collections import OrderedDict


def test_add_feed_factory_adds_factory(factory, rando, gov):
    tx = factory.addFeedFactory(rando, {"from": gov})

    # check feed factory added to registry
    assert factory.isFeedFactory(rando) is True

    # check event emitted
    assert 'FeedFactoryAdded' in tx.events
    expect_event = OrderedDict({"user": gov.address, "feedFactory": rando})
    actual_event = tx.events['FeedFactoryAdded']
    assert actual_event == expect_event


def test_add_feed_factory_reverts_when_not_gov(factory, charlie, alice):
    # check reverts when non governor account attempts to add
    with reverts("OVLV1: !governor"):
        _ = factory.addFeedFactory(charlie, {"from": alice})


def test_add_feed_factory_reverts_when_factory_already_exists(factory,
                                                              feed_factory,
                                                              gov):
    assert factory.isFeedFactory(feed_factory) is True

    # check reverts when already supporting factory
    with reverts("OVLV1: feed factory already supported"):
        _ = factory.addFeedFactory(feed_factory, {"from": gov})


def test_remove_feed_factory_removes_feed_factory(factory, rando, gov):
    assert factory.isFeedFactory(rando) is True

    tx = factory.removeFeedFactory(rando, {"from": gov})

    assert 'FeedFactoryRemoved' in tx.events
    expect_event = OrderedDict({"user": gov.address, "feedFactory": rando})
    actual_event = tx.events['FeedFactoryRemoved']
    assert actual_event == expect_event


def test_remove_feed_factory_reverts_when_not_gov(factory, rando, gov):
    _ = factory.addFeedFactory(rando, {"from": gov})

    assert factory.isFeedFactory(rando) is True

    with reverts("OVLV1: !governor"):
        _ = factory.removeFeedFactory(rando, {"from": rando})


def test_remove_feed_factory_reverts_when_not_feed_factory(factory,
                                                           alice,
                                                           gov):
    with reverts("OVLV1: address not feed factory"):
        _ = factory.removeFeedFactory(alice, {"from": gov})
