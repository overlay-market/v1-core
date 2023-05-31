import pytest
from brownie import chain, reverts
from decimal import Decimal
from math import exp
from pytest import approx

from .utils import calculate_position_info, RiskParameter


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
        14,  # expect_average_block_time
    ]

    for i in range(len(RiskParameter)):
        # set the risk param
        expect_param = expect_params[i]
        market.setRiskParam(i, expect_param, {"from": factory})

        # check was actually set
        actual_param = market.params(i)
        assert expect_param == actual_param

        # undo tx for params to revert to conftest.py market state
        chain.undo()


def test_set_risk_param_pays_funding(market, feed, factory, ovl, alice):
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
        14,  # expect_average_block_time
    ]

    # build some positions
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

    # input values for build
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 2**256-1 if is_long else 0

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(market, approve_collateral, {"from": alice})
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     input_price_limit, {"from": alice})

    # cache prior oi, timestamp update last values
    prior_oi_long = market.oiLong()
    prior_oi_short = market.oiShort()
    prior_timestamp_update_last = market.timestampUpdateLast()

    for i in range(len(RiskParameter)):
        # mine the chain forward for some funding
        dt = 604800
        chain.mine(timestamp=prior_timestamp_update_last+dt)

        # get the expected oi BEFORE risk param set
        # to check that new k value (if set k) isn't used in oiAfterFunding
        # i.e. market updated before risk param set
        time_elapsed = dt

        # NOTE: oiAfterFunding() tests in test_funding.py
        if (prior_oi_long > prior_oi_short):
            expect_oi_long, expect_oi_short = market.oiAfterFunding(
                prior_oi_long, prior_oi_short, time_elapsed)
        else:
            expect_oi_short, expect_oi_long = market.oiAfterFunding(
                prior_oi_short, prior_oi_long, time_elapsed)

        # set the risk param
        expect_param = expect_params[i]
        tx = market.setRiskParam(i, expect_param, {"from": factory})

        # check expect funding calc used correct now time given chain mine
        timestamp_now = chain[tx.block_number]['timestamp']
        expect_timestamp_update_last = timestamp_now

        # get actual updated storage vars
        actual_timestamp_update_last = market.timestampUpdateLast()
        actual_oi_long = market.oiLong()
        actual_oi_short = market.oiShort()

        assert actual_timestamp_update_last == expect_timestamp_update_last
        assert actual_timestamp_update_last != prior_timestamp_update_last

        assert int(expect_oi_long) == approx(int(actual_oi_long))
        assert int(expect_oi_short) == approx(int(actual_oi_short))

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
    # idx for delta, cap_leverage, maintenance, liquidation fee rate
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_lfr = RiskParameter.LIQUIDATION_FEE_RATE.value

    tol = 1e-4

    # get other relevant risk params
    cap_leverage = Decimal(market.params(idx_cap_leverage)) / Decimal(1e18)
    mmf = Decimal(market.params(idx_mmf)) / Decimal(1e18)
    lfr = Decimal(market.params(idx_lfr)) / Decimal(1e18)
    max_delta = (1/cap_leverage - mmf/(1-lfr)) / Decimal(2.0)

    # check reverts when delta just above max
    input_delta = int(max_delta * Decimal(1e18) * Decimal(1 + tol))
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_delta, input_delta, {"from": factory})

    # check doesn't revert when delta just below max
    input_delta = int(max_delta * Decimal(1e18) * Decimal(1 - tol))
    market.setRiskParam(idx_delta, input_delta, {"from": factory})

    expect = input_delta
    actual = market.params(idx_delta)
    assert expect == actual


def test_set_cap_leverage_reverts_when_max_lev_liquidatable(market, factory):
    # idx for delta, cap_leverage, maintenance, liquidation fee rate
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_lfr = RiskParameter.LIQUIDATION_FEE_RATE.value

    tol = 1e-4

    # get other relevant risk params
    delta = Decimal(market.params(idx_delta)) / Decimal(1e18)
    mmf = Decimal(market.params(idx_mmf)) / Decimal(1e18)
    lfr = Decimal(market.params(idx_lfr)) / Decimal(1e18)
    max_cap_leverage = 1/(mmf/(1-lfr) + 2 * delta)

    # check reverts when one cap leverage greater than max
    input_cap_leverage = int(max_cap_leverage * Decimal(1e18) * Decimal(1+tol))
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_cap_leverage, input_cap_leverage,
                            {"from": factory})

    # check doesn't revert when cap leverage less than max
    input_cap_leverage = int(max_cap_leverage * Decimal(1e18) * Decimal(1-tol))
    market.setRiskParam(idx_cap_leverage, input_cap_leverage,
                        {"from": factory})

    expect = input_cap_leverage
    actual = market.params(idx_cap_leverage)
    assert expect == actual


def test_set_maintenance_margin_fraction_reverts_when_max_lev_liquidatable(
    market, factory
):
    # idx for delta, cap_leverage, maintenance, liquidation fee rate
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_lfr = RiskParameter.LIQUIDATION_FEE_RATE.value

    tol = 1e-4

    # get other relevant risk params
    cap_leverage = Decimal(market.params(idx_cap_leverage)) / Decimal(1e18)
    delta = Decimal(market.params(idx_delta)) / Decimal(1e18)
    lfr = Decimal(market.params(idx_lfr)) / Decimal(1e18)
    max_mmf = (1 / cap_leverage - 2 * delta) * (1-lfr)

    # check reverts when mmf greater than max
    input_mmf = int(max_mmf * Decimal(1e18) * Decimal(1 + tol))
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_mmf, input_mmf, {"from": factory})

    # check doesn't revert when maitenance margin fraction less than max
    input_mmf = int(max_mmf * Decimal(1e18) * Decimal(1 - tol))
    market.setRiskParam(idx_mmf, input_mmf, {"from": factory})

    expect = input_mmf
    actual = market.params(idx_mmf)
    assert expect == actual


def test_set_liquidation_fee_rate_reverts_when_max_lev_liquidatable(
    market, factory
):
    # idx for delta, cap_leverage, maintenance, liquidation fee rate
    idx_delta = RiskParameter.DELTA.value
    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_lfr = RiskParameter.LIQUIDATION_FEE_RATE.value

    tol = 1e-4

    # get other relevant risk params
    cap_leverage = Decimal(market.params(idx_cap_leverage)) / Decimal(1e18)
    delta = Decimal(market.params(idx_delta)) / Decimal(1e18)
    mmf = Decimal(market.params(idx_mmf)) / Decimal(1e18)
    max_lfr = 1 - mmf / (1 / cap_leverage - 2 * delta)

    # check reverts when greater than liquidationFeeRate max
    input_lfr = int(max_lfr * Decimal(1e18) * Decimal(1 + tol))
    with reverts("OVLV1: max lev immediately liquidatable"):
        market.setRiskParam(idx_lfr, input_lfr, {"from": factory})

    # check doesn't revert when liquidation fee rate less than max
    input_lfr = int(max_lfr * Decimal(1e18) * Decimal(1 - tol))
    market.setRiskParam(idx_lfr, input_lfr, {"from": factory})

    expect = input_lfr
    actual = market.params(idx_lfr)
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
