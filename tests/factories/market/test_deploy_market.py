from brownie import chain, interface, reverts
from collections import OrderedDict


# NOTE: Use feed_one in successful create market test. Use feed_two for revert
# tests


def test_deploy_market_creates_market(factory, feed_factory, feed_one, ovl,
                                      gov):
    # NOTE: feed_one will have a successfully deployed market on it for
    # remainder of test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_one

    # risk params
    expect_k = 8587500000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000

    # deploy market
    tx = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_k,
        expect_lmbda,
        expect_delta,
        expect_cap_payoff,
        expect_cap_oi,
        expect_cap_leverage,
        expect_maintenance_margin,
        expect_maintenance_margin_burn_rate,
        expect_trading_fee_rate,
        expect_min_collateral,
        {"from": gov}
    )
    # TODO: check returned address matches market
    expect_market = tx.return_value

    # check market added to registry
    actual_market = factory.getMarket(expect_feed)
    assert expect_market == actual_market
    assert factory.isMarket(expect_market) is True

    # check market granted mint/burn roles on ovl
    assert ovl.hasRole(ovl.MINTER_ROLE(), actual_market) is True
    assert ovl.hasRole(ovl.BURNER_ROLE(), actual_market) is True

    # check event emitted
    assert 'MarketDeployed' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": expect_market,
        "feed": expect_feed
    })
    actual_event = tx.events['MarketDeployed']
    assert actual_event == expect_event

    # check contract deployed with correct constructor params
    market_contract = interface.IOverlayV1Market(actual_market)

    # check immutables set in constructor
    assert market_contract.ovl() == ovl
    assert market_contract.feed() == expect_feed
    assert market_contract.factory() == factory

    # check risk params set in constructor
    assert market_contract.k() == expect_k
    assert market_contract.lmbda() == expect_lmbda
    assert market_contract.delta() == expect_delta
    assert market_contract.capPayoff() == expect_cap_payoff
    assert market_contract.capOi() == expect_cap_oi
    assert market_contract.capLeverage() == expect_cap_leverage
    assert market_contract.maintenanceMargin() == expect_maintenance_margin
    assert market_contract.maintenanceMarginBurnRate() \
        == expect_maintenance_margin_burn_rate
    assert market_contract.tradingFeeRate() == expect_trading_fee_rate
    assert market_contract.minCollateral() == expect_min_collateral

    # check trading fee recipient is factory
    assert market_contract.tradingFeeRecipient() == factory

    # check funding paid last timestamp is last block's
    assert market_contract.fundingPaidLast() \
        == chain[tx.block_number]['timestamp']


def test_deploy_market_reverts_when_not_gov(factory, feed_factory, feed_two,
                                            rando):
    # NOTE: feed_two will NOT have a successfully deployed market on it
    # in test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 8587500000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000

    # check can't deploy from rando account
    with reverts("OVLV1: !governor"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_k,
            expect_lmbda,
            expect_delta,
            expect_cap_payoff,
            expect_cap_oi,
            expect_cap_leverage,
            expect_maintenance_margin,
            expect_maintenance_margin_burn_rate,
            expect_trading_fee_rate,
            expect_min_collateral,
            {"from": rando}
        )


def test_deploy_market_reverts_when_market_already_exists(factory,
                                                          feed_factory,
                                                          feed_one, gov):
    # NOTE: feed_one has a successfully deployed market on it given
    # test_deploy_market_creates_market above in test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_one

    assert factory.getMarket(feed_one) \
        != "0x0000000000000000000000000000000000000000"

    # risk params
    expect_k = 8587500000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000

    # check can't deploy from rando account
    with reverts("OVLV1: market already exists"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_k,
            expect_lmbda,
            expect_delta,
            expect_cap_payoff,
            expect_cap_oi,
            expect_cap_leverage,
            expect_maintenance_margin,
            expect_maintenance_margin_burn_rate,
            expect_trading_fee_rate,
            expect_min_collateral,
            {"from": gov}
        )


def test_deploy_market_reverts_when_feed_factory_not_supported(factory, rando,
                                                               feed_two, gov):
    # NOTE: feed_two will NOT have a successfully deployed market on it
    # in test_deploy_market.py
    expect_feed_factory = rando
    expect_feed = feed_two

    # risk params
    expect_k = 8587500000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000

    # check can't deploy with rando factory feed
    with reverts("OVLV1: feed factory not supported"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_k,
            expect_lmbda,
            expect_delta,
            expect_cap_payoff,
            expect_cap_oi,
            expect_cap_leverage,
            expect_maintenance_margin,
            expect_maintenance_margin_burn_rate,
            expect_trading_fee_rate,
            expect_min_collateral,
            {"from": gov}
        )


def test_deploy_market_reverts_when_feed_does_not_exist(factory, feed_factory,
                                                        rando, gov):
    expect_feed_factory = feed_factory
    expect_feed = rando

    # risk params
    expect_k = 8587500000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000

    # check can't deploy with rando feed not in factory feed registry
    with reverts("OVLV1: feed does not exist"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_k,
            expect_lmbda,
            expect_delta,
            expect_cap_payoff,
            expect_cap_oi,
            expect_cap_leverage,
            expect_maintenance_margin,
            expect_maintenance_margin_burn_rate,
            expect_trading_fee_rate,
            expect_min_collateral,
            {"from": gov}
        )
