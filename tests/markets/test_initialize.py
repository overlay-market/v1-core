import pytest
from brownie import reverts, OverlayV1Market
from decimal import Decimal
from math import exp
from pytest import approx

from .utils import RiskParameter


# NOTE: Tests passing with isolation fixture
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_initialize_creates_market(fake_deployer, ovl, fake_feed,
                                   fake_factory, gov):
    # risk params
    k = 1220000000000
    lmbda = 1000000000000000000
    delta = 2500000000000000
    cap_payoff = 5000000000000000000
    cap_notional = 800000000000000000000000
    cap_leverage = 5000000000000000000
    circuit_breaker_window = 2592000
    circuit_breaker_mint_target = 66670000000000000000000
    maintenance_margin_fraction = 100000000000000000
    maintenance_margin_burn_rate = 100000000000000000
    liquidation_fee_rate = 10000000000000000
    trading_fee_rate = 750000000000000
    min_collateral = 100000000000000
    price_drift_upper_limit = 100000000000000
    average_block_time = 14

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit, average_block_time]

    # deploy the market from the deployer
    tx = fake_deployer.deploy(fake_feed, {"from": fake_factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # check market deployed correctly with immutables
    assert market.ovl() == ovl
    assert market.feed() == fake_feed
    assert market.factory() == fake_factory

    # initialize market with risk params
    market.initialize(params, {"from": fake_factory})

    # check market deployed correctly with risk params
    expect_params = params
    actual_params = [market.params(i) for i in range(len(RiskParameter))]
    assert expect_params == actual_params

    # check risk calc cached for price drift upper limit
    data = fake_feed.latest()
    (_, _, macro_window, _, _, _, _, _) = data
    drift = Decimal(price_drift_upper_limit) / Decimal(1e18)
    pow = drift * Decimal(macro_window)
    expect_drift = int(Decimal(exp(pow)) * Decimal(1e18))
    actual_drift = market.dpUpperLimit()
    assert expect_drift == approx(actual_drift)


def test_initialize_reverts_when_not_factory(fake_deployer, fake_feed,
                                             fake_factory, rando):
    # risk params
    params = [
        2220000000000,  # expect_k
        500000000000000000,  # expect_lmbda
        5000000000000000,  # expect_delta
        7000000000000000000,  # expect_cap_payoff
        900000000000000000000000,  # expect_cap_notional
        4000000000000000000,  # expect_cap_leverage
        3592000,  # expect_circuit_breaker_window
        96670000000000000000000,  # expect_circuit_breaker_mint_target
        50000000000000000,  # expect_maintenance_margin_fraction
        200000000000000000,  # expect_maintenance_margin_burn_rate
        5000000000000000,  # expect_liquidation_fee_rate
        250000000000000,  # expect_trading_fee_rate
        500000000000000,  # expect_min_collateral
        50000000000000,  # expect_price_drift_upper_limit
        14,  # expect_average_block_time
    ]

    # deploy the market from the deployer
    tx = fake_deployer.deploy(fake_feed, {"from": fake_factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # attempt to initialize not from factory
    with reverts("OVLV1: !factory"):
        _ = market.initialize(params, {"from": rando})


def test_initialize_reverts_when_price_is_zero(ovl, fake_deployer, fake_feed,
                                               fake_factory, gov):
    # risk params
    k = 1220000000000
    lmbda = 1000000000000000000
    delta = 2500000000000000
    cap_payoff = 5000000000000000000
    cap_notional = 800000000000000000000000
    cap_leverage = 5000000000000000000
    circuit_breaker_window = 2592000
    circuit_breaker_mint_target = 66670000000000000000000
    maintenance_margin_fraction = 100000000000000000
    maintenance_margin_burn_rate = 100000000000000000
    liquidation_fee_rate = 10000000000000000
    trading_fee_rate = 750000000000000
    min_collateral = 100000000000000
    price_drift_upper_limit = 100000000000000
    average_block_time = 14

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit, average_block_time]

    # deploy the market from the deployer
    tx = fake_deployer.deploy(fake_feed, {"from": fake_factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # set mock feed price to zero
    price = 0
    fake_feed.setPrice(price, {"from": gov})

    # check can not deploy the market
    with reverts("OVLV1:!data"):
        market.initialize(params, {"from": fake_factory})


def test_deploy_reverts_when_max_leverage_is_liquidatable(ovl, fake_feed,
                                                          fake_deployer,
                                                          fake_factory,
                                                          gov):
    # risk params
    k = 1220000000000
    lmbda = 1000000000000000000
    delta = 2500000000000000
    cap_payoff = 5000000000000000000
    cap_notional = 800000000000000000000000
    cap_leverage = 5000000000000000000
    circuit_breaker_window = 2592000
    circuit_breaker_mint_target = 66670000000000000000000
    maintenance_margin_fraction = 200000000000000000
    maintenance_margin_burn_rate = 100000000000000000
    liquidation_fee_rate = 10000000000000000
    trading_fee_rate = 750000000000000
    min_collateral = 100000000000000
    price_drift_upper_limit = 100000000000000
    average_block_time = 14

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit, average_block_time]

    # deploy the market from the deployer
    tx = fake_deployer.deploy(fake_feed, {"from": fake_factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # check can not deploy the market
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.initialize(params, {"from": fake_factory})


def test_deploy_reverts_when_price_drift_exceeds_max_exp(ovl, fake_feed,
                                                         fake_deployer,
                                                         fake_factory,
                                                         gov):
    # risk params
    k = 1220000000000
    lmbda = 1000000000000000000
    delta = 2500000000000000
    cap_payoff = 5000000000000000000
    cap_notional = 800000000000000000000000
    cap_leverage = 5000000000000000000
    circuit_breaker_window = 2592000
    circuit_breaker_mint_target = 66670000000000000000000
    maintenance_margin_fraction = 100000000000000000
    maintenance_margin_burn_rate = 100000000000000000
    liquidation_fee_rate = 10000000000000000
    trading_fee_rate = 750000000000000
    min_collateral = 100000000000000
    price_drift_upper_limit = 100000000000000000
    average_block_time = 14

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit, average_block_time]

    # deploy the market from the deployer
    tx = fake_deployer.deploy(fake_feed, {"from": fake_factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # check can not deploy the market
    with reverts("OVLV1: price drift exceeds max exp"):
        market.initialize(params, {"from": fake_factory})
