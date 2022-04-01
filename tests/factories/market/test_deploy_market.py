import pytest
from copy import copy
from brownie import chain, reverts, OverlayV1Market
from collections import OrderedDict


# NOTE: Use feed_one in successful create market test. Use feed_two for revert
# tests. feed_three has already had a market deployed on it (market fixture)
# Using isolation fixture given successfully deploy markets in some tests
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_deploy_market_creates_market(factory, feed_factory, feed_one, ovl,
                                      minter_role, burner_role, gov):
    # NOTE: feed_one will have a successfully deployed market on it for
    # remainder of test_deploy_market.py
    expect_feed_factory = feed_factory
    expect_feed = feed_one

    # risk params
    expect_k = 1220000000000
    expect_lmbda = 1000000000000000000
    expect_delta = 2500000000000000
    expect_cap_payoff = 5000000000000000000
    expect_cap_notional = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_fraction = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_liquidation_fee_rate = 10000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 100000000000000
    expect_average_block_time = 14

    expect_params = [expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_notional, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin_fraction,
                     expect_maintenance_margin_burn_rate,
                     expect_liquidation_fee_rate, expect_trading_fee_rate,
                     expect_min_collateral, expect_price_drift_upper_limit,
                     expect_average_block_time]

    # deploy market
    tx = factory.deployMarket(
        expect_feed_factory,
        expect_feed,
        expect_params,
        {"from": gov}
    )
    # check returned address matches market
    expect_market = tx.return_value

    # check market added to registry
    actual_market = factory.getMarket(expect_feed)
    assert expect_market == actual_market
    assert factory.isMarket(expect_market) is True

    # check market granted mint/burn roles on ovl
    assert ovl.hasRole(minter_role, actual_market) is True
    assert ovl.hasRole(burner_role, actual_market) is True

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
    market_contract = OverlayV1Market.at(actual_market)

    # check immutables set in constructor
    assert market_contract.ovl() == ovl
    assert market_contract.feed() == expect_feed
    assert market_contract.factory() == factory

    # check risk params set in constructor
    actual_params = [market_contract.params(i) for i in range(15)]
    assert expect_params == actual_params

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
    expect_cap_notional = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_fraction = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_liquidation_fee_rate = 10000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 100000000000000
    expect_average_block_time = 14

    expect_params = [expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_notional, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin_fraction,
                     expect_maintenance_margin_burn_rate,
                     expect_liquidation_fee_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit,
                     expect_average_block_time]

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
    expect_cap_notional = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_fraction = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_liquidation_fee_rate = 10000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 100000000000000
    expect_average_block_time = 14

    expect_params = [expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_notional, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin_fraction,
                     expect_maintenance_margin_burn_rate,
                     expect_liquidation_fee_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit,
                     expect_average_block_time]

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
    expect_cap_notional = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_fraction = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_liquidation_fee_rate = 10000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 100000000000000
    expect_average_block_time = 14

    expect_params = [expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_notional, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin_fraction,
                     expect_maintenance_margin_burn_rate,
                     expect_liquidation_fee_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit,
                     expect_average_block_time]

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
    expect_cap_notional = 800000000000000000000000
    expect_cap_leverage = 5000000000000000000
    expect_circuit_breaker_window = 2592000
    expect_circuit_breaker_mint_target = 66670000000000000000000
    expect_maintenance_margin_fraction = 100000000000000000
    expect_maintenance_margin_burn_rate = 100000000000000000
    expect_liquidation_fee_rate = 10000000000000000
    expect_trading_fee_rate = 750000000000000
    expect_min_collateral = 100000000000000
    expect_price_drift_upper_limit = 100000000000000
    expect_average_block_time = 14

    expect_params = [expect_k, expect_lmbda, expect_delta, expect_cap_payoff,
                     expect_cap_notional, expect_cap_leverage,
                     expect_circuit_breaker_window,
                     expect_circuit_breaker_mint_target,
                     expect_maintenance_margin_fraction,
                     expect_maintenance_margin_burn_rate,
                     expect_liquidation_fee_rate,
                     expect_trading_fee_rate, expect_min_collateral,
                     expect_price_drift_upper_limit,
                     expect_average_block_time]

    # check can't deploy with rando feed not in factory feed registry
    with reverts("OVLV1: feed does not exist"):
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )


# risk param out of bounds tests
def test_deploy_market_reverts_when_param_less_than_min(factory, feed_factory,
                                                        feed_one, feed_two,
                                                        gov):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # default risk params
    default_params = [
        1220000000000,  # expect_k
        1000000000000000000,  # expect_lmbda
        1500000000000000,  # expect_delta
        5000000000000000000,  # expect_cap_payoff
        800000000000000000000000,  # expect_cap_notional
        3000000000000000000,  # expect_cap_leverage
        2592000,  # expect_circuit_breaker_window
        66670000000000000000000,  # expect_circuit_breaker_mint_target
        10000000000000000,  # expect_maintenance_margin_fraction
        100000000000000000,  # expect_maintenance_margin_burn_rate
        10000000000000000,  # expect_liquidation_fee_rate
        750000000000000,  # expect_trading_fee_rate
        100000000000000,  # expect_min_collateral
        100000000000000,  # expect_price_drift_upper_limit
        14,  # expect_average_block_time
    ]

    for i in range(len(default_params)):
        # reset to the defaults first
        expect_params = copy(default_params)

        # check can't deploy with param less than min
        expect_param = factory.PARAMS_MIN(i) - 1
        if expect_param >= 0:
            expect_params[i] = expect_param
            with reverts("OVLV1: param out of bounds"):
                _ = factory.deployMarket(
                    expect_feed_factory,
                    expect_feed,
                    expect_params,
                    {"from": gov}
                )

        # check deploys with param equal to min
        expect_param = factory.PARAMS_MIN(i)
        expect_params[i] = expect_param
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

        # undo the tx so can try to redeploy new market for next param
        chain.undo()


def test_deploy_market_reverts_when_param_greater_than_max(factory, feed_one,
                                                           feed_two, gov,
                                                           feed_factory):
    expect_feed_factory = feed_factory
    expect_feed = feed_two

    # default risk params
    default_params = [
        1220000000000,  # expect_k
        1000000000000000000,  # expect_lmbda
        1500000000000000,  # expect_delta
        5000000000000000000,  # expect_cap_payoff
        800000000000000000000000,  # expect_cap_notional
        3000000000000000000,  # expect_cap_leverage
        2592000,  # expect_circuit_breaker_window
        66670000000000000000000,  # expect_circuit_breaker_mint_target
        10000000000000000,  # expect_maintenance_margin_fraction
        100000000000000000,  # expect_maintenance_margin_burn_rate
        10000000000000000,  # expect_liquidation_fee_rate
        750000000000000,  # expect_trading_fee_rate
        100000000000000,  # expect_min_collateral
        100000000000000,  # expect_price_drift_upper_limit
        14,  # expect_average_block_time
    ]

    for i in range(len(default_params)):
        # reset to the defaults first
        expect_params = copy(default_params)

        # check can't deploy with param greater than max
        expect_param = factory.PARAMS_MAX(i) + 1
        expect_params[i] = expect_param
        with reverts("OVLV1: param out of bounds"):
            _ = factory.deployMarket(
                expect_feed_factory,
                expect_feed,
                expect_params,
                {"from": gov}
            )

        # check deploys with param equal to max
        expect_param = factory.PARAMS_MAX(i)
        expect_params[i] = expect_param
        _ = factory.deployMarket(
            expect_feed_factory,
            expect_feed,
            expect_params,
            {"from": gov}
        )

        # undo the tx so can try to redeploy new market for next param
        chain.undo()
