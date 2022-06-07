from pytest import approx
from brownie.test import given, strategy


@given(oi=strategy('uint96', min_value="1"),
       oi_total=strategy('uint96', min_value="1"),
       oi_total_shares=strategy('uint96', min_value="1"))
def test_calc_oi_shares(position, oi, oi_total, oi_total_shares):
    expect = int(oi * oi_total_shares / oi_total)
    actual = position.calcOiShares(oi, oi_total, oi_total_shares)
    assert expect == approx(actual)


def test_calc_oi_shares_when_oi_total_zero(position):
    oi = 10000000000000000000  # 10
    oi_total = 0
    oi_total_shares = 0

    expect = oi
    actual = position.calcOiShares(oi, oi_total, oi_total_shares)
    assert expect == actual

    # try with rounding issue remaining
    oi_total = 0
    oi_total_shares = 1

    expect = oi
    actual = position.calcOiShares(oi, oi_total, oi_total_shares)
    assert expect == actual


def test_calc_oi_shares_when_oi_total_shares_zero(position):
    oi = 10000000000000000000  # 10
    oi_total = 0
    oi_total_shares = 0

    expect = oi
    actual = position.calcOiShares(oi, oi_total, oi_total_shares)
    assert expect == actual

    # try with rounding issue remaining
    oi_total = 1
    oi_total_shares = 0

    expect = oi
    actual = position.calcOiShares(oi, oi_total, oi_total_shares)
    assert expect == actual
