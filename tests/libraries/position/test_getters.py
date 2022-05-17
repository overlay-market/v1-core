from pytest import approx
from decimal import Decimal

from .utils import price_to_tick


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

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oiShares * fraction
    fraction = 1000000000000000000  # 1
    expect = int(oi_shares * (fraction_remaining / 1e4)
                 * (fraction / 1e18))  # 0.064
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

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check oiShares * fraction
    fraction = 250000000000000000  # 0.25
    expect = int(oi_shares * (fraction_remaining / 1e4)
                 * (fraction / 1e18))  # 0.016
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


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
