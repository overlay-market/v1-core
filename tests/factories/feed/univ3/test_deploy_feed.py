from brownie import interface, reverts
from collections import OrderedDict


def test_deploy_feed_creates_quanto_feed(factory, pool_uniweth_30bps, uni,
                                         pool_daiweth_30bps, dai, weth,
                                         alice):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18

    tx = factory.deployFeed(market_pool, market_base_token, market_quote_token,
                            market_base_amount, {"from": alice})
    actual_feed = tx.return_value

    # check feed is added to registry
    assert factory.getFeed(market_pool, market_base_token, market_quote_token,
                           market_base_amount) == actual_feed
    assert factory.isFeed(actual_feed) is True

    # check event emitted
    assert 'FeedDeployed' in tx.events
    expect_event = OrderedDict({"user": alice.address, "feed": actual_feed})
    actual_event = tx.events['FeedDeployed']
    assert actual_event == expect_event

    # check contract deployed with correct constructor params
    feed_contract = interface.IOverlayV1UniswapV3Feed(actual_feed)
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.ovlWethPool() == ovlweth_pool
    assert feed_contract.ovl() == ovl
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount


def test_deploy_feed_creates_inverse_feed(factory, pool_uniweth_30bps, uni,
                                          weth, alice):
    market_pool = pool_uniweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = weth
    market_quote_token = uni
    market_base_amount = 1000000000000000000  # 1e18

    tx = factory.deployFeed(market_pool, market_base_token, market_quote_token,
                            market_base_amount, {"from": alice})
    actual_feed = tx.return_value

    # check feed is added to registry
    assert factory.getFeed(market_pool, market_base_token, market_quote_token,
                           market_base_amount) == actual_feed
    assert factory.isFeed(actual_feed) is True

    # check event emitted
    assert 'FeedDeployed' in tx.events
    expect_event = OrderedDict({"user": alice.address, "feed": actual_feed})
    actual_event = tx.events['FeedDeployed']
    assert actual_event == expect_event

    # check contract deployed with correct constructor params
    feed_contract = interface.IOverlayV1UniswapV3Feed(actual_feed)
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.ovlWethPool() == ovlweth_pool
    assert feed_contract.ovl() == ovl
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount


def test_deploy_feed_reverts_when_feed_already_exits(factory, uni, dai, weth,
                                                     pool_daiweth_30bps,
                                                     pool_uniweth_30bps,
                                                     alice):
    market_pool = pool_daiweth_30bps
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18

    with reverts("OVLV1: feed already exists"):
        _ = factory.deployFeed(market_pool, market_base_token,
                               market_quote_token, market_base_amount,
                               {"from": alice})
