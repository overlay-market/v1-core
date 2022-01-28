import pytest
from brownie import chain, interface, reverts
from collections import OrderedDict


# TODO: fix for priceDriftUpperLimit addition, add deployer tests


# NOTE: Use feed_one in successful create market test. Use feed_two for revert
# tests. feed_three has already had a market deployed on it (market fixture)
# Using isolation fixture given successfully deploy markets in some tests
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_deploy_market_creates_market(factory, feed_factory, feed_one, ovl,
                                      gov):
    # NOTE: feed_one will have a successfully deployed market on it for
    # remainder of test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_one

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)

    # deploy market
    tx = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
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
    assert market_contract.priceDriftUpperLimit() == \
        expect_price_drift_upper_limit

    # check trading fee recipient is factory
    assert market_contract.tradingFeeRecipient() == factory

    # check update last timestamp is last block's
    assert market_contract.timestampUpdateLast() \
        == chain[tx.block_number]['timestamp']


def test_deploy_market_reverts_when_not_gov(factory, feed_factory, feed_two,
                                            rando):
    # NOTE: feed_two will NOT have a successfully deployed market on it
    # in test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)

    # check can't deploy from rando account
    with reverts("OVLV1: !governor"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": rando}
        )


def test_deploy_market_reverts_when_market_already_exists(factory,
                                                          feed_factory,
                                                          feed_three, gov):
    # NOTE: feed_one has a successfully deployed market on it given
    # test_deploy_market_creates_market above in test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_three

    assert factory.getMarket(feed_three) \
        != "0x0000000000000000000000000000000000000000"

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)

    # check can't deploy from rando account
    with reverts("OVLV1: market already exists"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )


def test_deploy_market_reverts_when_feed_factory_not_supported(factory, rando,
                                                               feed_two, gov):
    # NOTE: feed_two will NOT have a successfully deployed market on it
    # in test_deploy_market.py
    expect_feed_factory = rando
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)

    # check can't deploy with rando factory feed
    with reverts("OVLV1: feed factory not supported"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )


def test_deploy_market_reverts_when_feed_does_not_exist(factory, feed_factory,
                                                        rando, gov):
    expect_feed_factory = feed_factory
    expect_feed = rando

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)

    # check can't deploy with rando feed not in factory feed registry
    with reverts("OVLV1: feed does not exist"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )


# risk param out of bounds tests

# k tests
def test_deploy_market_reverts_when_k_less_than_min(factory, feed_factory,
                                                    feed_one, feed_two, gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with k less than min
    expect_k = factory.MIN_K() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: k out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with k equal to min
    expect_k = factory.MIN_K()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_k_greater_than_max(factory, feed_factory,
                                                       feed_one, feed_two,
                                                       gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with k greater than max
    expect_k = factory.MAX_K() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: k out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with k equal to max
    expect_k = factory.MAX_K()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# lmbda tests
def test_deploy_market_reverts_when_lmbda_less_than_min(factory, feed_factory,
                                                        feed_one, feed_two,
                                                        gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with lmbda less than min
    expect_lmbda = factory.MIN_LMBDA() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: lmbda out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with lmbda equal to min
    expect_lmbda = factory.MIN_LMBDA()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_lmbda_greater_than_max(factory,
                                                           feed_factory,
                                                           feed_one, feed_two,
                                                           gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with lmbda greater than max
    expect_lmbda = factory.MAX_LMBDA() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: lmbda out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with lmbda equal to max
    expect_lmbda = factory.MAX_LMBDA()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# delta tests
def test_deploy_market_reverts_when_delta_less_than_min(factory, feed_factory,
                                                        feed_one, feed_two,
                                                        gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with delta less than min
    expect_delta = factory.MIN_DELTA() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: delta out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with delta equal to min
    expect_delta = factory.MIN_DELTA()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_delta_greater_than_max(factory,
                                                           feed_factory,
                                                           feed_one, feed_two,
                                                           gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with delta greater than max
    expect_delta = factory.MAX_DELTA() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: delta out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with delta equal to max
    expect_delta = factory.MAX_DELTA()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# capPayoff tests
def test_deploy_market_reverts_when_cap_payoff_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with capPayoff less than min
    expect_cap_payoff = factory.MIN_CAP_PAYOFF() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: capPayoff out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with capPayoff equal to min
    expect_cap_payoff = factory.MIN_CAP_PAYOFF()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_cap_payoff_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with capPayoff greater than max
    expect_cap_payoff = factory.MAX_CAP_PAYOFF() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: capPayoff out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with capPayoff equal to max
    expect_cap_payoff = factory.MAX_CAP_PAYOFF()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# capOi tests
# NOTE: no cap_oi_less_than_min test because MIN_CAP_OI is zero
def test_deploy_market_reverts_when_cap_oi_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with capOi greater than max
    expect_cap_oi = factory.MAX_CAP_OI() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: capOi out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with capOi equal to max
    expect_cap_oi = factory.MAX_CAP_OI()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# capLeverage tests
def test_deploy_market_reverts_when_cap_leverage_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with capLeverage less than min
    expect_cap_leverage = factory.MIN_CAP_LEVERAGE() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: capLeverage out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with capLeverage equal to min
    expect_cap_leverage = factory.MIN_CAP_LEVERAGE()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_cap_leverage_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with capLeverage greater than max
    expect_cap_leverage = factory.MAX_CAP_LEVERAGE() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: capLeverage out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with capLeverage equal to max
    expect_cap_leverage = factory.MAX_CAP_LEVERAGE()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# circuitBreakerWindow tests
def test_deploy_market_reverts_when_circuit_breaker_window_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with circuitBreakerWindow less than min
    expect_circuit_breaker_window = factory.MIN_CIRCUIT_BREAKER_WINDOW() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: circuitBreakerWindow out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with circuitBreakerWindow equal to min
    expect_circuit_breaker_window = factory.MIN_CIRCUIT_BREAKER_WINDOW()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_circuit_breaker_window_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with circuitBreakerWindow greater than max
    expect_circuit_breaker_window = factory.MAX_CIRCUIT_BREAKER_WINDOW() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: circuitBreakerWindow out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with circuitBreakerWindow equal to max
    expect_circuit_breaker_window = factory.MAX_CIRCUIT_BREAKER_WINDOW()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# circuitBreakerMintTarget tests
def test_deploy_market_reverts_when_circuit_breaker_target_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with circuitBreakerWindow greater than max
    expect_circuit_breaker_mint_target = \
        factory.MAX_CIRCUIT_BREAKER_MINT_TARGET() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: circuitBreakerMintTarget out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with circuitBreakerWindow equal to max
    expect_circuit_breaker_mint_target = \
        factory.MAX_CIRCUIT_BREAKER_MINT_TARGET()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# maintenanceMargin tests
def test_deploy_market_reverts_when_maintenance_margin_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with maintenanceMargin less than min
    expect_maintenance_margin = factory.MIN_MAINTENANCE_MARGIN() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: maintenanceMargin out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with maintenanceMargin equal to min
    expect_maintenance_margin = factory.MIN_MAINTENANCE_MARGIN()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_maintenance_margin_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with maintenanceMargin greater than max
    expect_maintenance_margin = factory.MAX_MAINTENANCE_MARGIN() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: maintenanceMargin out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with maintenanceMargin equal to max
    expect_maintenance_margin = factory.MAX_MAINTENANCE_MARGIN()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# maintenanceMarginBurnRate tests
def test_deploy_market_reverts_when_maintenance_margin_burn_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with maintenanceMarginBurnRate less than min
    expect_maintenance_margin_burn_rate = \
        factory.MIN_MAINTENANCE_MARGIN_BURN_RATE() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: maintenanceMarginBurnRate out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with maintenanceMargin equal to min
    expect_maintenance_margin_burn_rate = \
        factory.MIN_MAINTENANCE_MARGIN_BURN_RATE()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_maintenance_margin_burn_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with maintenanceMargin greater than max
    expect_maintenance_margin_burn_rate = \
        factory.MAX_MAINTENANCE_MARGIN_BURN_RATE() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: maintenanceMarginBurnRate out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with maintenanceMarginBurnRate equal to max
    expect_maintenance_margin_burn_rate = \
        factory.MAX_MAINTENANCE_MARGIN_BURN_RATE()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# tradingFeeRate tests
def test_deploy_market_reverts_when_trading_fee_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with tradingFeeRate less than min
    expect_trading_fee_rate = factory.MIN_TRADING_FEE_RATE() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: tradingFeeRate out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with tradingFeeRate equal to min
    expect_trading_fee_rate = factory.MIN_TRADING_FEE_RATE()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_trading_fee_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with tradingFeeRate greater than max
    expect_trading_fee_rate = factory.MAX_TRADING_FEE_RATE() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: tradingFeeRate out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with tradingFeeRate equal to max
    expect_trading_fee_rate = factory.MAX_TRADING_FEE_RATE()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


# minCollateral tests
def test_deploy_market_reverts_when_min_collateral_less_than_min(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with minCollateral less than min
    expect_min_collateral = factory.MIN_MINIMUM_COLLATERAL() - 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: minCollateral out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with minCollateral equal to min
    expect_min_collateral = factory.MIN_MINIMUM_COLLATERAL()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )


def test_deploy_market_reverts_when_min_collateral_greater_than_max(
    factory,
    feed_factory,
    feed_one,
    feed_two,
    gov
):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_oi = 800000000000000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_price_drift_upper_limit = 1000000000000000000

    # check can't deploy with minCollateral greater than max
    expect_min_collateral = factory.MAX_MINIMUM_COLLATERAL() + 1
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    with reverts("OVLV1: minCollateral out of bounds"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

    # check deploys with minCollateral equal to max
    expect_min_collateral = factory.MAX_MINIMUM_COLLATERAL()
    expect_params = (expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_oi, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin,
                     expect_maintenance_margin_burn_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit)
    _ = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )
