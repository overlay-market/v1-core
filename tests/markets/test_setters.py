import pytest
from brownie import chain, reverts
from decimal import Decimal
from math import exp
from pytest import approx

from .utils import RiskParameter


# NOTE: Use isolation fixture to avoid possible revert with max
# NOTE: lev immediately liquidatable market check
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_set_risk_param(market, factory):
    # risk params
    expect_params = [
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
    ]

    for i in range(len(expect_params)):
        # set the risk param
        expect_param = expect_params[i]
        market.setRiskParam(i, expect_param, {"from": factory})

        # check was actually set
        actual_param = market.params(i)
        assert expect_param == actual_param

        # undo tx for params to revert to conftest.py market state
        chain.undo()


def test_set_risk_param_caches_calc(market, feed, factory):
    # set the risk param
    expect_param = 50000000000000
    idx_drift = RiskParameter.PRICE_DRIFT_UPPER_LIMIT.value
    market.setRiskParam(idx_drift, expect_param, {"from": factory})

    # check was actually set
    actual_param = market.params(idx_drift)
    assert expect_param == actual_param

    # check was actually cached
    data = feed.latest()
    (_, _, macro_window, _, _, _, _, _) = data
    drift = Decimal(expect_param) / Decimal(1e18)
    pow = drift * Decimal(macro_window)
    expect = int(Decimal(exp(pow)) * Decimal(1e18))
    actual = market.dpUpperLimit()
    assert expect == approx(actual)


def test_set_risk_param_reverts_when_not_factory(market, alice):
    expect_k = 2220000000000
    with reverts("OVLV1: !factory"):
        _ = market.setRiskParam(0, expect_k, {"from": alice})


def test_set_delta_reverts_when_max_lev_liquidatable(market, factory):
    # idx for delta, cap_leverage, maintenance are, respectively: 2, 5, 8
    # in enum Risk.Parameters
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value

    # get other relevant risk params
    cap_leverage = Decimal(market.params(idx_cap_leverage)) / Decimal(1e18)
    mmf = Decimal(market.params(idx_mmf)) / Decimal(1e18)
    max_delta = (1/cap_leverage - mmf) / Decimal(2.0)

    # check reverts when one more than max
    input_delta = int(max_delta * Decimal(1e18)) + 1
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_delta, input_delta, {"from": factory})

    # check doesn't revert when delta equal to max
    input_delta -= 1
    market.setRiskParam(idx_delta, input_delta, {"from": factory})

    expect = input_delta
    actual = market.params(idx_delta)
    assert expect == actual


def test_set_cap_leverage_reverts_when_max_lev_liquidatable(market, factory):
    # idx for delta, cap_leverage, maintenance are, respectively: 2, 5, 8
    # in enum Risk.Parameters
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value

    # get other relevant risk params
    delta = Decimal(market.params(idx_delta)) / Decimal(1e18)
    mmf = Decimal(market.params(idx_mmf)) / Decimal(1e18)
    max_cap_leverage = 1/(mmf + 2 * delta)

    # check reverts when one more than max
    input_cap_leverage = int(max_cap_leverage * Decimal(1e18)) + 1
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_cap_leverage, input_cap_leverage,
                            {"from": factory})

    # check doesn't revert when cap leverage equal to max
    input_cap_leverage -= 1
    market.setRiskParam(idx_cap_leverage, input_cap_leverage,
                        {"from": factory})

    expect = input_cap_leverage
    actual = market.params(idx_cap_leverage)
    assert expect == actual


def test_set_maintenance_margin_fraction_reverts_when_max_lev_liquidatable(
    market, factory
):
    # idx for delta, cap_leverage, maintenance are, respectively: 2, 5, 8
    # in enum Risk.Parameters
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value

    # get other relevant risk params
    cap_leverage = Decimal(market.params(idx_cap_leverage)) / Decimal(1e18)
    delta = Decimal(market.params(idx_delta)) / Decimal(1e18)
    max_mmf = 1 / cap_leverage - 2 * delta

    # check reverts when one more than max
    input_mmf = int(max_mmf * Decimal(1e18)) + 1
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_mmf, input_mmf, {"from": factory})

    # check doesn't revert when maitenance margin fraction equal to max
    input_mmf -= 1
    market.setRiskParam(idx_mmf, input_mmf, {"from": factory})

    expect = input_mmf
    actual = market.params(idx_mmf)
    assert expect == actual


def test_set_price_drift_upper_limit_reverts_when_exceeds_max_exp(
    market, feed, factory
):
    # idx for price drift upper limit is: 13
    # in enum Risk.Parameters
    idx_price_drift_upper_limit = RiskParameter.PRICE_DRIFT_UPPER_LIMIT.value

    _, _, macro_window, _, _, _, _, _ = feed.latest()
    max_exp = 20000000000000000000
    max_price_drift_upper_limit = int(Decimal(max_exp)/Decimal(macro_window)) \
        + 1

    # check reverts when one more than max
    with reverts("OVLV1: price drift exceeds max exp"):
        market.setRiskParam(
            idx_price_drift_upper_limit, max_price_drift_upper_limit,
            {"from": factory})

    # check doesn't revert when price drift equal to max
    max_price_drift_upper_limit -= 1
    market.setRiskParam(
        idx_price_drift_upper_limit, max_price_drift_upper_limit,
        {"from": factory})

    expect = max_price_drift_upper_limit
    actual = market.params(idx_price_drift_upper_limit)
    assert expect == actual
