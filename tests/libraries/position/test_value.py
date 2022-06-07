from pytest import approx
from decimal import Decimal

from .utils import price_to_tick


def test_value(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 5000  # 0.5

    current_price = 150000000000000000000  # 150
    mid_price = 100000000000000000000  # 100
    entry_price = 100000000000000000000  # 100

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.05
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.04

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check value is oi * entry_price - debt + oi*(current_price - entry_price)
    # when long
    is_long = True
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 6500000000000000000  # 6.5
    actual = position.value(pos, fraction, oi, oi_shares, current_price,
                            cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1.05e-4)

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 1500000000000000000  # 1.5
    actual = position.value(pos, fraction, oi, oi_shares, current_price,
                            cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1.05e-4)


def test_value_when_entry_not_equal_to_mid(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 10000  # 1

    current_price = 150000000000000000000  # 150
    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * current_price - debt
    # when long
    is_long = True
    entry_price = 110000000000000000000  # 110
    entry_tick = price_to_tick(entry_price)

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 12000000000000000000  # 12
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1.05e-4)

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    entry_price = 95000000000000000000  # 95
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 2500000000000000000  # 2.5
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1.05e-4)


def test_value_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 5000  # 0.5

    current_price = 150000000000000000000  # 150
    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.05
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.04

    # inputs for position function
    fraction = 500000000000000000  # 0.5
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * current_price - debt
    # when long
    is_long = True
    entry_price = 110000000000000000000  # 110
    entry_tick = price_to_tick(entry_price)

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 3000000000000000000  # 3
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1.05e-4)

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    entry_price = 95000000000000000000  # 95
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 625000000000000000  # 0.625
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1.05e-4)


def test_value_when_payoff_greater_than_cap(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 10000  # 1.0

    entry_price = 101000000000000000000  # 101
    mid_price = 100000000000000000000  # 100
    current_price = 800000000000000000000  # 800

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    # check value is
    # oi * entry_price * (1 + cap_payoff) - debt + q - oi * entry_price
    # when long
    expect = 58500000000000000000
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)

    # NOTE: rel tol of 1.00e-4 given tick has precision to 1bps
    assert expect == approx(actual, rel=1e-4)


def test_value_when_underwater(position):
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    liquidated = False
    fraction_remaining = 10000  # 1.0

    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value returns zero when long is underwater
    is_long = True
    entry_price = 101000000000000000000  # 101
    entry_tick = price_to_tick(entry_price)
    current_price = 75000000000000000000  # 75

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)
    assert expect == actual

    # check value returns zero when short is underwater
    is_long = False
    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)
    current_price = 125000000000000000000  # 125

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)
    assert expect == actual


def test_value_when_fraction_remaining_zero(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 0  # 0

    current_price = 150000000000000000000  # 150
    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.05
    oi_shares = 0  # 0

    # inputs for position function
    fraction = 500000000000000000  # 0.5
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * current_price - debt
    # when long
    is_long = True
    entry_price = 110000000000000000000  # 110
    entry_tick = price_to_tick(entry_price)

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0  # 0
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)
    assert expect == actual

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    entry_price = 95000000000000000000  # 95
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0  # 0
    actual = position.value(pos, fraction, oi, oi_shares,
                            current_price, cap_payoff)
    assert expect == actual
