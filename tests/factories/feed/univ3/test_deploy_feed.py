from brownie import (
    reverts, OverlayV1UniswapV3Feed, OverlayV1NoReserveUniswapV3Feed
)
from collections import OrderedDict


def test_deploy_feed_creates_quanto_feed_without_reserve(
        factory_without_reserve, pool_daiweth_30bps, dai, weth, alice):

    market_pool = pool_daiweth_30bps
    market_fee = 3000

    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1e18

    tx = factory_without_reserve.deployFeed(market_base_token,
                                            market_quote_token,
                                            market_fee,
                                            market_base_amount,
                                            {'from': alice})

    actual_feed = tx.return_value

    assert factory_without_reserve.getFeed(
        market_pool, market_base_token, market_base_amount) == actual_feed
    assert factory_without_reserve.isFeed(actual_feed) is True

    assert 'FeedDeployed' in tx.events
    expect_event = OrderedDict({"user": alice.address, "feed": actual_feed})
    actual_event = tx.events['FeedDeployed']
    assert actual_event == expect_event

    feed_contract = OverlayV1NoReserveUniswapV3Feed.at(actual_feed)
    assert feed_contract.feedFactory() == factory_without_reserve
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount


def test_deploy_feed_creates_quanto_feed(factory, pool_uniweth_30bps, uni,
                                         pool_daiweth_30bps, dai, weth,
                                         alice):
    market_pool = pool_daiweth_30bps
    ovweth_pool = pool_uniweth_30bps
    market_fee = 3000
    ovweth_fee = 3000
    ov = uni
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18
    ovweth_base_token = ov
    ovweth_quote_token = weth

    tx = factory.deployFeed(market_base_token, market_quote_token, market_fee,
                            market_base_amount, ovweth_base_token,
                            ovweth_quote_token, ovweth_fee, {"from": alice})
    actual_feed = tx.return_value

    # check feed is added to registry
    assert factory.getFeed(market_pool, market_base_token, market_base_amount,
                           ovweth_pool) == actual_feed
    assert factory.isFeed(actual_feed) is True

    # check event emitted
    assert 'FeedDeployed' in tx.events
    expect_event = OrderedDict({"user": alice.address, "feed": actual_feed})
    actual_event = tx.events['FeedDeployed']
    assert actual_event == expect_event

    # check contract deployed with correct constructor params
    feed_contract = OverlayV1UniswapV3Feed.at(actual_feed)
    assert feed_contract.feedFactory() == factory
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.ovXPool() == ovweth_pool
    assert feed_contract.ov() == ov
    assert feed_contract.x() == weth
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount


def test_deploy_feed_creates_inverse_feed(factory, pool_uniweth_30bps, uni,
                                          weth, alice):
    market_pool = pool_uniweth_30bps
    ovweth_pool = pool_uniweth_30bps
    market_fee = 3000
    ovweth_fee = 3000
    ov = uni
    market_base_token = weth
    market_quote_token = ov
    market_base_amount = 1000000000000000000  # 1e18
    ovweth_base_token = weth
    ovweth_quote_token = ov

    tx = factory.deployFeed(market_base_token, market_quote_token, market_fee,
                            market_base_amount, ovweth_base_token,
                            ovweth_quote_token, ovweth_fee, {"from": alice})
    actual_feed = tx.return_value

    # check feed is added to registry
    assert factory.getFeed(market_pool, market_base_token, market_base_amount,
                           ovweth_pool) == actual_feed
    assert factory.isFeed(actual_feed) is True

    # check event emitted
    assert 'FeedDeployed' in tx.events
    expect_event = OrderedDict({"user": alice.address, "feed": actual_feed})
    actual_event = tx.events['FeedDeployed']
    assert actual_event == expect_event

    # check contract deployed with correct constructor params
    feed_contract = OverlayV1UniswapV3Feed.at(actual_feed)
    assert feed_contract.feedFactory() == factory
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.ovXPool() == ovweth_pool
    assert feed_contract.ov() == ov
    assert feed_contract.x() == weth
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount


def test_deploy_no_reserve_feed_reverts_when_market_pool_not_exists(
        factory_without_reserve, alice, bob, pool_daiweth_30bps, dai, weth):

    market_base_amount = 1000000000000000000  # 1e18

    # check reverts when base token not in pool
    market_fee = 3000
    market_base_token = bob
    market_quote_token = dai
    with reverts("OVV1: !marketPool"):
        _ = factory_without_reserve.deployFeed(
                market_base_token, market_quote_token,
                market_fee, market_base_amount, {"from": alice})

    # check reverts when quote token not in pool
    market_fee = 3000
    market_base_token = weth
    market_quote_token = bob
    with reverts("OVV1: !marketPool"):
        _ = factory_without_reserve.deployFeed(
                market_base_token, market_quote_token,
                market_fee, market_base_amount, {"from": alice})

    # check reverts when fee not in pool
    market_fee = 215
    market_base_token = weth
    market_quote_token = dai
    with reverts("OVV1: !marketPool"):
        _ = factory_without_reserve.deployFeed(
                market_base_token, market_quote_token,
                market_fee, market_base_amount, {"from": alice})


def test_deploy_feed_reverts_when_market_pool_not_exists(factory, alice, bob,
                                                         pool_daiweth_30bps,
                                                         pool_uniweth_30bps,
                                                         uni, dai, weth):
    market_base_amount = 1000000000000000000  # 1e18
    ovweth_fee = 3000
    ov = uni
    ovweth_base_token = ov
    ovweth_quote_token = weth

    # check reverts when base token not in pool
    market_fee = 3000
    market_base_token = bob
    market_quote_token = dai
    with reverts("OVV1: !marketPool"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})

    # check reverts when quote token not in pool
    market_fee = 3000
    market_base_token = weth
    market_quote_token = bob
    with reverts("OVV1: !marketPool"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})

    # check reverts when fee not in pool
    market_fee = 215
    market_base_token = weth
    market_quote_token = dai
    with reverts("OVV1: !marketPool"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})


def test_deploy_feed_reverts_when_ovx_pool_not_exists(factory, alice, bob,
                                                       pool_daiweth_30bps,
                                                       pool_uniweth_30bps,
                                                       uni, dai, weth):
    market_fee = 3000
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18

    # check reverts when base token not in pool
    ovweth_fee = 3000
    ovweth_base_token = bob
    ovweth_quote_token = weth
    with reverts("OVV1: !ovXPool"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})

    # check reverts when quote token not in pool
    ovweth_fee = 3000
    ovweth_base_token = uni
    ovweth_quote_token = bob
    with reverts("OVV1: !ovXPool"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})

    # check reverts when fee not in pool
    ovweth_fee = 215
    ovweth_base_token = uni
    ovweth_quote_token = weth
    with reverts("OVV1: !ovXPool"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})


def test_deploy_no_reserve_feed_reverts_when_feed_already_exists(
        factory_without_reserve, dai,
        weth, pool_daiweth_30bps, alice):

    market_pool = pool_daiweth_30bps
    market_fee = 3000
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18

    # Check feed already exists first from prior unit test above
    feed = factory_without_reserve.getFeed(market_pool,
                                           market_base_token,
                                           market_base_amount)
    assert factory_without_reserve.isFeed(feed) is True

    # check reverts when attempt to deploy again
    with reverts("OVV1: feed already exists"):
        _ = factory_without_reserve.deployFeed(
                                        market_base_token,
                                        market_quote_token,
                                        market_fee,
                                        market_base_amount, {"from": alice})


def test_deploy_feed_reverts_when_feed_already_exists(factory, uni, dai, weth,
                                                      pool_daiweth_30bps,
                                                      pool_uniweth_30bps,
                                                      alice):
    market_pool = pool_daiweth_30bps
    ovweth_pool = pool_uniweth_30bps
    market_fee = 3000
    ovweth_fee = 3000
    ov = uni
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18
    ovweth_base_token = weth
    ovweth_quote_token = ov

    # Check feed already exists first from prior unit test above
    feed = factory.getFeed(market_pool, market_base_token, market_base_amount,
                           ovweth_pool)
    assert factory.isFeed(feed) is True

    # check reverts when attempt to deploy again
    with reverts("OVV1: feed already exists"):
        _ = factory.deployFeed(market_base_token, market_quote_token,
                               market_fee, market_base_amount,
                               ovweth_base_token, ovweth_quote_token,
                               ovweth_fee, {"from": alice})
