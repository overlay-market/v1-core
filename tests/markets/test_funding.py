from pytest import approx
from brownie.test import given, strategy
from decimal import Decimal
from math import exp, sqrt

from .utils import RiskParameter


@given(
    oi_long=strategy('decimal', min_value='0.001', max_value='800000',
                     places=3),
    oi_short=strategy('decimal', min_value='0.001', max_value='800000',
                      places=3),
    dt=strategy('uint256', min_value='0', max_value='2592000'))
def test_oi_after_funding(market, oi_long, oi_short, dt):
    oi_long = oi_long * Decimal(1e18)
    oi_short = oi_short * Decimal(1e18)
    oi_overweight = oi_long if oi_long >= oi_short else oi_short
    oi_underweight = oi_short if oi_long >= oi_short else oi_long

    oi = oi_overweight + oi_underweight
    oi_imb = oi_overweight - oi_underweight

    # calculate expected oi values long and short
    k = Decimal(market.params(RiskParameter.K.value)) / Decimal(1e18)
    expect_oi = oi * Decimal(
        sqrt(1 - (oi_imb/oi)**2 * Decimal(1 - exp(-4*k*dt))))
    expect_oi_imb = oi_imb * Decimal(exp(-2*k*dt))

    expect_oi_overweight = int((expect_oi + expect_oi_imb) / 2)
    expect_oi_underweight = int((expect_oi - expect_oi_imb) / 2)

    # get actual oi values long and short
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt)

    # check expect oi values equal actual oi values after funding
    assert int(actual_oi_overweight) == approx(expect_oi_overweight)
    assert int(actual_oi_underweight) == approx(expect_oi_underweight)


@given(
    oi_overweight=strategy('decimal', min_value='0.001', max_value='800000',
                           places=3),
    dt=strategy('uint256', min_value='0', max_value='2592000'))
def test_oi_after_funding_when_underweight_is_zero(market, oi_overweight, dt):
    oi_overweight = oi_overweight * Decimal(1e18)
    oi_underweight = 0

    oi_imb = oi_overweight

    # calculate expected oi values long and short
    k = Decimal(market.params(RiskParameter.K.value)) / Decimal(1e18)
    expect_oi_imb = oi_imb * Decimal(exp(-2*k*dt))

    # overweight gets drawn down
    expect_oi_overweight = int(expect_oi_imb)
    expect_oi_underweight = 0

    # get actual oi values long and short
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt)

    # check expect oi values equal actual oi values after funding
    assert int(actual_oi_overweight) == approx(expect_oi_overweight)
    assert int(actual_oi_underweight) == approx(expect_oi_underweight)


def test_oi_after_funding_when_longs_and_shorts_are_zero(market):
    oi_long = 0
    oi_short = 0
    dt = 600

    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_long, oi_short, dt)

    # should remain zero
    assert actual_oi_overweight == 0
    assert actual_oi_underweight == 0


@given(
    oi_long=strategy('decimal', min_value='0.001', max_value='800000',
                     places=3),
    oi_short=strategy('decimal', min_value='0.001', max_value='800000',
                      places=3))
def test_oi_after_funding_when_dt_infinite(market, oi_long, oi_short):
    # let time go to "infinity"
    oi_long = oi_long * Decimal(1e18)
    oi_short = oi_short * Decimal(1e18)
    oi_overweight = oi_long if oi_long >= oi_short else oi_short
    oi_underweight = oi_short if oi_long >= oi_short else oi_long

    oi = oi_overweight + oi_underweight
    oi_imb = oi_overweight - oi_underweight

    tol = 1e-4

    # calculate time elapsed needed to get a MAX_NATURAL_EXPONENT in
    # imb drawdown power
    max_exponent = Decimal(20)
    k = Decimal(market.params(RiskParameter.K.value)) / Decimal(1e18)
    dt = (max_exponent / (2 * k)) * Decimal(1 + tol)

    # calculate expected oi values long and short
    expect_oi = Decimal(sqrt(oi**2 - oi_imb**2))
    expect_oi_imb = 0

    expect_oi_overweight = int((expect_oi + expect_oi_imb) / 2)
    expect_oi_underweight = int((expect_oi - expect_oi_imb) / 2)

    # check actual equals expected
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt)

    assert int(actual_oi_overweight) == approx(expect_oi_overweight)
    assert int(actual_oi_underweight) == approx(expect_oi_underweight)

    # check no reverts if before "infinite" time elapsed power
    dt = (max_exponent / (2 * k)) * Decimal(1 - tol)
    _, _ = market.oiAfterFunding(oi_overweight, oi_underweight, dt)


def test_oi_after_funding_when_underweight_is_zero_dt_infinite(market):
    # all oi should be to overweight side and let time go to "infinity"
    # to test edge case of oiOverWeightNow => 0
    oi_overweight = Decimal(10 * 1e18)
    oi_underweight = 0

    tol = 1e-4

    # calculate time elapsed needed to get a MAX_NATURAL_EXPONENT in
    # imb drawdown power
    max_exponent = Decimal(20)
    k = Decimal(market.params(RiskParameter.K.value)) / Decimal(1e18)
    dt = (max_exponent / (2 * k)) * Decimal(1 + tol)

    # overweight gets drawn down to zero if beyond "infinite" time elasped
    # alongside underweight (i.e. all contracts burned)
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt)

    assert actual_oi_overweight == 0
    assert actual_oi_underweight == 0

    # check overweight != 0 if before "infinite" time elapsed power
    dt = (max_exponent / (2 * k)) * Decimal(1 - tol)
    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_overweight, oi_underweight, dt)

    assert actual_oi_underweight == 0
    assert actual_oi_overweight > 0
