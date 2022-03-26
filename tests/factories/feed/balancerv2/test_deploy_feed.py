from brownie import interface
from collections import OrderedDict


def test_deploy_feed_creates_quanto_feed(factory, weth, bal, dai, alice,
                                         pool_balweth, pool_daiweth,
                                         balv2_tokens):
    '''
    Tests that the deployFeed function in the OverlayV1BalancerV2Factory
    contract deploys a new feed successfully.

    Inputs:
      factory      [Contract]: OverlayV1BalancerV2Factory contract instance
      weth         [Contract]: WETH token contract instance
      bal          [Contract]: BAL token contract instance representing the OVL
                               token
      dai          [Contract]: DAI token contract instance
      alice        [Account]:  Brownie provided eth account address for Alice
                               the trader
      pool_balweth [Contract]: Balancer V2 WeightedPool2Tokens contract
                               instance for the BAL/WETH pool, representing the
                               OVL/WETH token pair
      pool_daiweth [Contract]: Balancer V2 WeightedPool2Tokens contract
                               instance for the DAI/WETH pool
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
    '''
    market_pool = pool_daiweth
    ovlweth_pool = pool_balweth
    ovl = bal
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000000000000000  # 1e18

    # TODO: check is not feed prior to deploy

    tx = factory.deployFeed(market_pool, market_base_token, market_quote_token,
                            market_base_amount, balv2_tokens, {"from": alice})
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
    feed_contract = interface.IOverlayV1BalancerV2Feed(actual_feed)
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.ovlWethPool() == ovlweth_pool
    assert feed_contract.ovl() == ovl
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount


def test_deploy_feed_creates_inverse_feed(factory, weth, bal, alice,
                                          pool_balweth, balv2_tokens):
    '''
    Tests that the deployFeed function in the OverlayV1BalancerV2Factory
    contract deploys a new inverse feed successfully.

    Inputs:
      factory      [Contract]: OverlayV1BalancerV2Factory contract instance
      weth         [Contract]: WETH token contract instance
      bal          [Contract]: BAL token contract instance representing the OVL
                               token
      alice        [Account]:  Brownie provided eth account address for Alice
                               the trader
      pool_balweth [Contract]: Balancer V2 WeightedPool2Tokens contract
                               instance for the BAL/WETH pool, representing the
                               OVL/WETH token pair
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
    '''
    market_pool = pool_balweth
    ovlweth_pool = pool_balweth
    ovl = bal
    market_base_token = weth
    market_quote_token = bal
    market_base_amount = 1000000000000000000  # 1e18

    # TODO: check is not feed prior to deploy

    balv2_tokens = (balv2_tokens[0], balv2_tokens[1], balv2_tokens[1])

    tx = factory.deployFeed(market_pool, market_base_token, market_quote_token,
                            market_base_amount, balv2_tokens, {"from": alice})
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
    feed_contract = interface.IOverlayV1BalancerV2Feed(actual_feed)
    assert feed_contract.marketPool() == market_pool
    assert feed_contract.ovlWethPool() == ovlweth_pool
    assert feed_contract.ovl() == ovl
    assert feed_contract.marketBaseToken() == market_base_token
    assert feed_contract.marketQuoteToken() == market_quote_token
    assert feed_contract.marketBaseAmount() == market_base_amount
