from pytest import approx
from brownie import reverts
from math import log
from brownie.test import given, strategy
from decimal import Decimal


@given(a=strategy('uint256', min_value='1', max_value=str(2**255-1)),
       b=strategy('uint256', min_value='1', max_value=str(2**255-1)))
def test_log_up(fixed_point, a, b):
    expect_a = Decimal(a) / Decimal(1e18)
    expect_b = Decimal(b) / Decimal(1e18)

    expect = int(Decimal(log(expect_a, expect_b)) * Decimal(1e18))
    actual = int(fixed_point.logUp(a, b))

    assert expect == approx(actual)
    assert expect <= actual  # check round up error added


def test_log_up_reverts_a_is_zero(fixed_point):
    a = 0
    b = 1
    with reverts("FixedPoint: a out of bounds"):
        fixed_point.logUp(a, b)


def test_log_up_reverts_a_gt_max(fixed_point):
    a = 2**255
    b = 1
    with reverts("FixedPoint: a out of bounds"):
        fixed_point.logUp(a, b)


def test_log_up_reverts_b_is_zero(fixed_point):
    a = 1
    b = 0
    with reverts("FixedPoint: b out of bounds"):
        fixed_point.logUp(a, b)


def test_log_up_reverts_b_is_gt_max(fixed_point):
    a = 1
    b = 2**255
    with reverts("FixedPoint: b out of bounds"):
        fixed_point.logUp(a, b)


@given(a=strategy('uint256', min_value='1', max_value=str(2**255-1)),
       b=strategy('uint256', min_value='1', max_value=str(2**255-1)))
def test_log_down(fixed_point, a, b):
    expect_a = Decimal(a) / Decimal(1e18)
    expect_b = Decimal(b) / Decimal(1e18)

    expect = int(Decimal(log(expect_a, expect_b)) * Decimal(1e18))
    actual = int(fixed_point.logDown(a, b))

    assert expect == approx(actual)
    assert expect >= actual  # check round down error subtracted


def test_log_down_reverts_a_is_zero(fixed_point):
    a = 0
    b = 1
    with reverts("FixedPoint: a out of bounds"):
        fixed_point.logDown(a, b)


def test_log_down_reverts_a_gt_max(fixed_point):
    a = 2**255
    b = 1
    with reverts("FixedPoint: a out of bounds"):
        fixed_point.logDown(a, b)


def test_log_down_reverts_b_is_zero(fixed_point):
    a = 1
    b = 0
    with reverts("FixedPoint: b out of bounds"):
        fixed_point.logDown(a, b)


def test_log_down_reverts_b_is_gt_max(fixed_point):
    a = 1
    b = 2**255
    with reverts("FixedPoint: b out of bounds"):
        fixed_point.logDown(a, b)
