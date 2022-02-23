import pytest
from brownie import reverts
from decimal import Decimal


# NOTE: Use isolation fixture to avoid possible revert with max
# NOTE: lev immediately liquidatable market check
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_set_k(market, factory):
    expect = 2220000000000
    market.setK(expect, {"from": factory})
    actual = market.k()
    assert expect == actual


def test_set_lmbda(market, factory):
    expect = 500000000000000000
    market.setLmbda(expect, {"from": factory})
    actual = market.lmbda()
    assert expect == actual


def test_set_delta(market, factory):
    expect = 5000000000000000
    market.setDelta(expect, {"from": factory})
    actual = market.delta()
    assert expect == actual


def test_set_delta_reverts_when_max_lev_liquidatable(market, factory):
    # get other relevant risk params
    maintenance_margin_fraction = \
        Decimal(market.maintenanceMarginFraction()) / Decimal(1e18)
    cap_leverage = Decimal(market.capLeverage()) / Decimal(1e18)
    max_delta = (1 / cap_leverage - maintenance_margin_fraction) / Decimal(2.0)

    # check reverts when one more than max
    input_delta = int(max_delta * Decimal(1e18)) + 1
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setDelta(input_delta, {"from": factory})

    # check doesn't revert when delta equal to max
    input_delta -= 1
    market.setDelta(input_delta, {"from": factory})

    expect = input_delta
    actual = market.delta()
    assert expect == actual


def test_set_cap_payoff(market, factory):
    expect = 7000000000000000000
    market.setCapPayoff(expect, {"from": factory})
    actual = market.capPayoff()
    assert expect == actual


def test_set_cap_notional(market, factory):
    expect = 900000000000000000000000
    market.setCapNotional(expect, {"from": factory})
    actual = market.capNotional()
    assert expect == actual


def test_set_cap_leverage(market, factory):
    expect = 4000000000000000000
    market.setCapLeverage(expect, {"from": factory})
    actual = market.capLeverage()
    assert expect == actual


def test_set_cap_leverage_reverts_when_max_lev_liquidatable(market, factory):
    # get other relevant risk params
    maintenance_margin_fraction = \
        Decimal(market.maintenanceMarginFraction()) / Decimal(1e18)
    delta = Decimal(market.delta()) / Decimal(1e18)
    max_cap_leverage = 1 / (maintenance_margin_fraction + 2 * delta)

    # check reverts when one more than max
    input_cap_leverage = int(max_cap_leverage * Decimal(1e18)) + 1
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setCapLeverage(input_cap_leverage, {"from": factory})

    # check doesn't revert when cap leverage equal to max
    input_cap_leverage -= 1
    market.setCapLeverage(input_cap_leverage, {"from": factory})

    expect = input_cap_leverage
    actual = market.capLeverage()
    assert expect == actual


def test_set_circuit_breaker_window(market, factory):
    expect = 3592000
    market.setCircuitBreakerWindow(expect, {"from": factory})
    actual = market.circuitBreakerWindow()
    assert expect == actual


def test_set_circuit_breaker_mint_target(market, factory):
    expect = 96670000000000000000000
    market.setCircuitBreakerMintTarget(expect, {"from": factory})
    actual = market.circuitBreakerMintTarget()
    assert expect == actual


def test_set_maintenance_margin_fraction(market, factory):
    expect = 50000000000000000
    market.setMaintenanceMarginFraction(expect, {"from": factory})
    actual = market.maintenanceMarginFraction()
    assert expect == actual


def test_set_maintenance_margin_fraction_reverts_when_max_lev_liquidatable(
    market, factory
):
    # get other relevant risk params
    cap_leverage = Decimal(market.capLeverage()) / Decimal(1e18)
    delta = Decimal(market.delta()) / Decimal(1e18)
    max_maintenance_margin_fraction = 1 / cap_leverage - 2 * delta

    # check reverts when one more than max
    input_maintenance_margin_fraction = int(
        max_maintenance_margin_fraction * Decimal(1e18)) + 1
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setMaintenanceMarginFraction(
            input_maintenance_margin_fraction, {"from": factory})

    # check doesn't revert when maitenance margin fraction equal to max
    input_maintenance_margin_fraction -= 1
    market.setMaintenanceMarginFraction(
        input_maintenance_margin_fraction, {"from": factory})

    expect = input_maintenance_margin_fraction
    actual = market.maintenanceMarginFraction()
    assert expect == actual


def test_set_maintenance_margin_burn_rate(market, factory):
    expect = 200000000000000000
    market.setMaintenanceMarginBurnRate(expect, {"from": factory})
    actual = market.maintenanceMarginBurnRate()
    assert expect == actual


def test_set_liquidation_fee_rate(market, factory):
    expect = 5000000000000000
    market.setLiquidationFeeRate(expect, {"from": factory})
    actual = market.liquidationFeeRate()
    assert expect == actual


def test_set_trading_fee_rate(market, factory):
    expect = 250000000000000
    market.setTradingFeeRate(expect, {"from": factory})
    actual = market.tradingFeeRate()
    assert expect == actual


def test_set_min_collateral(market, factory):
    expect = 500000000000000
    market.setMinCollateral(expect, {"from": factory})
    actual = market.minCollateral()
    assert expect == actual


def test_set_price_drift_upper_limit(market, factory):
    expect = 50000000000000
    market.setPriceDriftUpperLimit(expect, {"from": factory})
    actual = market.priceDriftUpperLimit()
    assert expect == actual


def test_set_price_drift_upper_limit_reverts_when_exceeds_max_exp(
    market, feed, factory
):
    _, _, macro_window, _, _, _, _, _ = feed.latest()
    max_exp = 20000000000000000000
    max_price_drift_upper_limit = int(Decimal(max_exp)/Decimal(macro_window)) \
        + 1

    # check reverts when one more than max
    with reverts("OVLV1: price drift exceeds max exp"):
        market.setPriceDriftUpperLimit(
            max_price_drift_upper_limit, {"from": factory})

    # check doesn't revert when price drift equal to max
    max_price_drift_upper_limit -= 1
    market.setPriceDriftUpperLimit(
        max_price_drift_upper_limit, {"from": factory})

    expect = max_price_drift_upper_limit
    actual = market.priceDriftUpperLimit()
    assert expect == actual


# TODO: setter revert tests when not factory
