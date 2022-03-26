import pytest
from brownie import reverts, OverlayV1Market

from .utils import RiskParameter


# NOTE: Tests passing with isolation fixture
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_deploy_creates_market(ovl, feed, factory, gov):
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

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit]

    # deploy the market
    market = gov.deploy(OverlayV1Market, ovl, feed, factory, params)

    # check market deployed correctly with immutables
    assert market.ovl() == ovl
    assert market.feed() == feed
    assert market.factory() == factory

    # check market deployed correctly with risk params
    expect_params = params
    actual_params = [market.params(i) for i in range(len(RiskParameter))]
    assert expect_params == actual_params


def test_deploy_reverts_when_price_is_zero(ovl, mock_feed, factory, gov):
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

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit]

    # set mock feed price to zero
    price = 0
    mock_feed.setPrice(price)

    # check can not deploy the market
    with reverts("OVLV1:!data"):
        gov.deploy(OverlayV1Market, ovl, mock_feed, factory, params)


def test_deploy_reverts_when_max_leverage_is_liquidatable(ovl, mock_feed,
                                                          factory, gov):
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

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit]

    # check can not deploy the market
    with reverts("OVLV1: max lev immediately liquidatable"):
        gov.deploy(OverlayV1Market, ovl, mock_feed, factory, params)


def test_deploy_reverts_when_price_drift_exceeds_max_exp(ovl, mock_feed,
                                                         factory, gov):
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

    params = [k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin_fraction, maintenance_margin_burn_rate,
              liquidation_fee_rate, trading_fee_rate, min_collateral,
              price_drift_upper_limit]

    # check can not deploy the market
    with reverts("OVLV1: price drift exceeds max exp"):
        gov.deploy(OverlayV1Market, ovl, mock_feed, factory, params)
