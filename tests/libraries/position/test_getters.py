from pytest import approx
from decimal import Decimal

from .utils import price_to_tick


# notionalInitial tests

def test_notional_initial(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    fraction = 1000000000000000000  # 1
    expect = int(notional * (fraction_remaining / 1e4) * (fraction / 1e18))
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual

    # check initial notional is oi * entry_price = notional
    # when short
    is_long = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = int(notional * (fraction_remaining / 1e4) * (fraction / 1e18))
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual


def test_notional_initial_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    fraction = 250000000000000000  # 0.25
    expect = int(notional * (fraction_remaining / 1e4) * (fraction / 1e18))
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual

    # check initial notional is oi * entry_price = notional
    # when short
    is_long = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = int(notional * (fraction_remaining / 1e4) * (fraction / 1e18))
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual


# oiInitial tests

def test_oi_initial(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oiInitial * fraction
    fraction = 1000000000000000000  # 1
    expect = int(oi * (fraction_remaining / 1e4) * (fraction / 1e18))  # 0.08
    actual = position.oiInitial(pos, fraction)

    # NOTE: rel tol of 1e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1e-4)


def test_oi_initial_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oiInitial * fraction
    fraction = 250000000000000000  # 0.25
    expect = int(oi * (fraction_remaining / 1e4) * (fraction / 1e18))  # 0.02
    actual = position.oiInitial(pos, fraction)

    # NOTE: rel tol of 1e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1e-4)


# oiSharesCurrent tests

def test_oi_shares_current(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oiShares * fraction
    fraction = 1000000000000000000  # 1
    expect = int(oi_shares * (fraction / 1e18))  # 0.064
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_oi_shares_current_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oiShares * fraction
    fraction = 250000000000000000  # 0.25
    expect = int(oi_shares * (fraction / 1e18))  # 0.016
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


# debtInitial tests

def test_debt_initial(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check debt * fraction
    fraction = 1000000000000000000  # 1
    expect = int(debt * (fraction_remaining / 1e4) * (fraction / 1e18))  # 1.6
    actual = position.debtInitial(pos, fraction)
    assert expect == actual


def test_debt_initial_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check debt * fraction
    fraction = 250000000000000000  # 0.25
    expect = int(debt * (fraction_remaining / 1e4) * (fraction / 1e18))  # 0.4
    actual = position.debtInitial(pos, fraction)
    assert expect == actual


# oiCurrent tests

def test_oi_current(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # total oi and oi shares on side
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    fraction = 1000000000000000000  # 1
    expect_oi = total_oi * (oi_shares / total_oi_shares)

    expect = int(expect_oi * (fraction / 1e18))
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual


def test_oi_current_is_initial_after_build(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 10000  # 1.0

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1

    # total oi and oi shares on side
    total_oi = 1200000000000000000  # 1.2
    total_oi_shares = 1500000000000000000  # 1.5
    oi_shares = int(Decimal(oi) * Decimal(total_oi_shares)
                    / Decimal(total_oi))  # 0.125

    # "build" the position
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # add to total oi and total oi shares
    total_oi += oi
    total_oi_shares += oi_shares

    # check oi is pro-rata shares of total oi
    fraction = 1000000000000000000  # 1
    expect_oi = total_oi * (oi_shares / total_oi_shares)
    expect = int(expect_oi * (fraction_remaining / 1e4) * (fraction / 1e18))

    actual_oi_initial = position.oiInitial(pos, fraction)
    actual_oi_current = position.oiCurrent(
        pos, fraction, total_oi, total_oi_shares)

    # NOTE: rel tol of 1e-4 given tick has precision to 1bps
    assert expect == approx(actual_oi_initial, rel=1e-4)
    assert expect == approx(actual_oi_current)


def test_oi_current_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # total oi and oi shares on side
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    fraction = 250000000000000000  # 0.25
    expect_oi = total_oi * (oi_shares / total_oi_shares)

    expect = int(expect_oi * (fraction / 1e18))
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
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction = 1000000000000000000  # 1

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # 1. lost it all due to funding (t -> infty)
    fraction_remaining = 10000  # 1.0
    total_oi = 0  # 0
    total_oi_shares = 15000000000000000000  # 15

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oi is zero
    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 2. unwound all of position oi
    fraction_remaining = 0  # 0
    oi_shares = 0  # 0
    total_oi = 4000000000000000000  # 4
    total_oi_shares = 5000000000000000000  # 5

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 3. all oi has been unwound
    oi_shares = 0  # 0
    fraction_remaining = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 0  # 0

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 4. position has been liquidated
    oi_shares = 0  # 0
    fraction_remaining = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 5000000000000000000  # 5
    liquidated = True

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 5. rounding error of some fraction remaining but no oi shares total
    oi_shares = 0  # 0
    fraction_remaining = 1  # 0.0001
    total_oi = 0  # 0
    total_oi_shares = 0  # 0
    liquidated = False

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual


# cost tests

def test_cost(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # cost is notional - debt
    cost = notional - debt

    # check cost * fraction
    fraction = 1000000000000000000  # 1
    expect = int(cost * (fraction_remaining / 1e4) * (fraction / 1e18))  # 6.4
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_cost_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # cost is notional - debt
    cost = notional - debt

    # check cost * fraction
    fraction = 250000000000000000  # 0.25
    expect = int(cost * (fraction_remaining / 1e4) * (fraction / 1e18))  # 1.6
    actual = position.cost(pos, fraction)
    assert expect == actual
