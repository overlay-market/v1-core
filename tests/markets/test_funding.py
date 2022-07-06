from pytest import approx
from brownie.test import given, strategy
from decimal import Decimal
from math import sqrt

from .utils import RiskParameter


@given(
    oi_long=strategy('decimal', min_value='0.001', max_value='800000',
                     places=3),
    oi_short=strategy('decimal', min_value='0.001', max_value='800000',
                      places=3),
    dt=strategy('uint256', min_value='0', max_value='2592000'),
    mid=strategy('decimal', min_value='0.01', max_value='1000000',
                 places=2))
def test_oi_after_funding(market, oi_long, oi_short, dt, mid):
    mid = mid * Decimal(1e18)
    oi_long = oi_long * Decimal(1e18)
    oi_short = oi_short * Decimal(1e18)
    oi_overweight = oi_long if oi_long >= oi_short else oi_short
    oi_underweight = oi_short if oi_long >= oi_short else oi_long

    oi = oi_overweight + oi_underweight
    oi_imb = oi_overweight - oi_underweight

    # get effective k
    k = Decimal(market.params(RiskParameter.K.value))
    cap_notional = Decimal(market.params(RiskParameter.CAP_NOTIONAL.value))
    cap_oi = Decimal(1e18) * cap_notional / mid
    q = oi_imb / cap_oi if oi_imb < cap_oi else Decimal(1.0)
    k_effective = k * q

    # get funding factor to draw down imbalance by
    k_effective = k_effective / Decimal(1e18)
    funding_factor = 1 / Decimal(1 + 2*k_effective*dt)

    # calculate expected oi values long and short
    if oi_imb > 0:
        expect_oi_imb = oi_imb * funding_factor
        expect_oi = oi * Decimal(
            sqrt(1 - (oi_imb/oi)**2 * Decimal(1 - (expect_oi_imb/oi_imb)**2)))
    else:
        expect_oi_imb = 0
        expect_oi = oi

    expect_oi_overweight = int((expect_oi + expect_oi_imb) / 2)
    expect_oi_underweight = int((expect_oi - expect_oi_imb) / 2)

    # get actual oi values long and short
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt, mid)

    # check expect oi values equal actual oi values after funding
    assert int(actual_oi_overweight) == approx(expect_oi_overweight)
    assert int(actual_oi_underweight) == approx(expect_oi_underweight)


@given(
    oi_overweight=strategy('decimal', min_value='0.001', max_value='800000',
                           places=3),
    dt=strategy('uint256', min_value='0', max_value='2592000'),
    mid=strategy('decimal', min_value='0.01', max_value='10', places=2))
def test_oi_after_funding_when_underweight_is_zero(market, oi_overweight, dt,
                                                   mid):
    oi_overweight = oi_overweight * Decimal(1e18)
    oi_underweight = 0
    mid = mid * Decimal(1e18)

    oi_imb = oi_overweight

    # get effective k
    k = Decimal(market.params(RiskParameter.K.value))
    cap_notional = Decimal(market.params(RiskParameter.CAP_NOTIONAL.value))
    cap_oi = Decimal(1e18) * cap_notional / mid
    q = oi_imb / cap_oi if oi_imb < cap_oi else Decimal(1.0)
    k_effective = k * q

    # get funding factor to draw down imbalance by
    k_effective = k_effective / Decimal(1e18)
    funding_factor = 1 / Decimal(1 + 2*k_effective*dt)

    # calculate expected oi values long and short
    expect_oi_imb = oi_imb * funding_factor

    # overweight gets drawn down
    expect_oi_overweight = int(expect_oi_imb)
    expect_oi_underweight = 0

    # get actual oi values long and short
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt, mid)

    # check expect oi values equal actual oi values after funding
    assert int(actual_oi_overweight) == approx(expect_oi_overweight)
    assert int(actual_oi_underweight) == approx(expect_oi_underweight)


def test_oi_after_funding_when_longs_and_shorts_are_zero(market):
    oi_long = 0
    oi_short = 0
    dt = 600
    mid = int(1e18)

    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_long, oi_short, dt, mid)

    # should remain zero
    assert actual_oi_overweight == 0
    assert actual_oi_underweight == 0


@given(
    oi_long=strategy('decimal', min_value='0.001', max_value='800000',
                     places=3),
    oi_short=strategy('decimal', min_value='0.001', max_value='800000',
                      places=3),
    mid=strategy('decimal', min_value='0.01', max_value='10', places=2))
def test_oi_after_funding_when_dt_infinite(market, oi_long, oi_short, mid):
    # let time go to "infinity"
    mid = mid * Decimal(1e18)
    oi_long = oi_long * Decimal(1e18)
    oi_short = oi_short * Decimal(1e18)
    oi_overweight = oi_long if oi_long >= oi_short else oi_short
    oi_underweight = oi_short if oi_long >= oi_short else oi_long

    oi = oi_overweight + oi_underweight
    oi_imb = oi_overweight - oi_underweight

    tol = 1e-4

    # get effective k
    k = Decimal(market.params(RiskParameter.K.value))
    cap_notional = Decimal(market.params(RiskParameter.CAP_NOTIONAL.value))
    cap_oi = Decimal(1e18) * cap_notional / mid
    q = oi_imb / cap_oi if oi_imb < cap_oi else Decimal(1.0)
    k_effective = k * q

    # calculate time elapsed needed to get a zero for funding factor
    max_denom = Decimal(1e36)
    max_dt = ((max_denom - Decimal(1e18))
              / (2 * k_effective)) if k_effective > 0 else 0
    dt = max_dt * Decimal(1 + tol)

    # calculate expected oi values long and short
    expect_oi = Decimal(sqrt(oi**2 - oi_imb**2))
    expect_oi_imb = 0

    expect_oi_overweight = int((expect_oi + expect_oi_imb) / 2)
    expect_oi_underweight = int((expect_oi - expect_oi_imb) / 2)

    # check actual equals expected
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt, mid)

    assert int(actual_oi_overweight) == approx(expect_oi_overweight)
    assert int(actual_oi_underweight) == approx(expect_oi_underweight)

    # check no reverts if before "infinite" time elapsed power
    dt = max_dt * Decimal(1-tol)
    _, _ = market.oiAfterFunding(oi_overweight, oi_underweight, dt, mid)


def test_oi_after_funding_when_underweight_is_zero_dt_infinite(market):
    # all oi should be to overweight side and let time go to "infinity"
    # to test edge case of oiOverWeightNow => 0
    oi_overweight = Decimal(100 * 1e18)
    oi_underweight = 0
    oi_imb = oi_overweight - oi_underweight
    mid = Decimal(1e18)

    tol = 1e-4

    # get effective k
    k = Decimal(market.params(RiskParameter.K.value))
    cap_notional = Decimal(market.params(RiskParameter.CAP_NOTIONAL.value))
    cap_oi = Decimal(1e18) * cap_notional / mid
    q = oi_imb / cap_oi if oi_imb < cap_oi else Decimal(1.0)
    k_effective = k * q

    # calculate time elapsed needed to get a zero for funding factor
    max_denom = Decimal(1e36)
    max_dt = ((max_denom - Decimal(1e18))
              / (2 * k_effective)) if k_effective > 0 else 0
    dt = max_dt * Decimal(1 + tol)

    # overweight gets drawn down to zero if beyond "infinite" time elasped
    # alongside underweight (i.e. all contracts burned)
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt, mid)

    assert actual_oi_overweight == 0
    assert actual_oi_underweight == 0

    # check overweight != 0 if before "infinite" time elapsed power
    dt = max_dt * Decimal(1 - tol)
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt, mid)

    assert actual_oi_underweight == 0
    assert actual_oi_overweight > 0
