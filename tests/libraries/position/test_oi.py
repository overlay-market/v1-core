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


def test_oi_current(position):
    # NOTE: oi = pos.oi_shares
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    fraction = 1000000000000000000  # 1

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # lost 3 from total oi due to funding
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    expect = int((total_oi * oi / total_oi_shares) * (fraction / 1e18))
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual


def test_oi_current_when_fraction_less_than_one(position):
    # NOTE: oi = pos.oi_shares
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    fraction = 250000000000000000  # 0.25

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # lost 3 from total oi due to funding
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    expect = int((total_oi * oi / total_oi_shares) * (fraction / 1e18))
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual


def test_oi_current_when_total_oi_or_oi_shares_zero(position):
    """
    Tests four possible cases of when oi should return 0

    Cases:
    1. total_oi = 0; oi_shares, total_oi_shares != 0
    2. oi_shares = 0; total_oi, total_oi_shares != 0
    3. oi_shares, total_oi, total_oi_shares = 0
    4. oi_shares, total_oi = 0; total_oi_shares != 0
    """
    # NOTE: oi = pos.oi_shares
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    debt = 2000000000000000000  # 2
    fraction = 1000000000000000000  # 1

    # 1. lost it all due to funding (t -> infty)
    notional = 10000000000000000000  # 10
    total_oi = 0  # 0
    total_oi_shares = 15000000000000000000  # 15
    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oi is zero
    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 2. unwound all of position oi
    notional = 0  # 0
    total_oi = 4000000000000000000  # 4
    total_oi_shares = 5000000000000000000  # 5
    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 3. all oi has been unwound
    notional = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 0  # 0
    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 4. position has been liquidated
    notional = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 5000000000000000000  # 5
    liquidated = True
    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual
