from pytest import approx
from brownie import reverts
from math import exp
from brownie.test import given, strategy
from decimal import Decimal


@given(x=strategy('decimal', min_value='0', max_value='40'))
def test_exp_up(fixed_point, x):
    x_fixed = int(x * Decimal(1e18))

    expect = int(Decimal(exp(x)) * Decimal(1e18))
    actual = fixed_point.expUp(x_fixed)

    assert expect == approx(actual)
    assert expect <= actual  # check round up error added


def test_exp_up_when_pow_is_zero(fixed_point):
    x = 0
    expect = 1000000000000000000
    actual = fixed_point.expUp(x)
    assert expect == actual


def test_exp_up_reverts_when_x_greater_than_int256(fixed_point):
    # check reverts when greater than int256 max
    x = 2**255
    with reverts("FixedPoint: x out of bounds"):
        fixed_point.expUp(x)


@given(x=strategy('decimal', min_value='0', max_value='40'))
def test_exp_down(fixed_point, x):
    x_fixed = int(x * Decimal(1e18))

    expect = int(Decimal(exp(x)) * Decimal(1e18))
    actual = fixed_point.expDown(x_fixed)

    assert expect == approx(actual)
    assert expect >= actual  # check round down error subtracted


def test_exp_down_when_pow_is_zero(fixed_point):
    x = 0
    expect = 1000000000000000000
    actual = fixed_point.expDown(x)
    assert expect == actual


def test_exp_down_reverts_when_x_greater_than_int256(fixed_point):
    # check reverts when greater than int256 max
    x = 2**255
    with reverts("FixedPoint: x out of bounds"):
        fixed_point.expDown(x)
