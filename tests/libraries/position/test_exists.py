from decimal import Decimal

from .utils import price_to_tick


def test_exists(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 10000  # 1 (4 decimal places for uint16)

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

    # check exists when not liquidated and fraction > 0
    expect = True
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_liquidated(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = True
    fraction_remaining = 0  # 0

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

    # check exists when liquidated
    expect = False
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_fraction_remaining_zero(position):
    # all of position has been unwound
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 0  # 0

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

    # check exists when not liquidated and fraction == 0
    expect = False
    actual = position.exists(pos)
    assert expect == actual

    # also check for the position that has all zero values
    zero_pos = (0, 0, 0, 0, False, False, 0, 0)
    expect = False
    actual = position.exists(zero_pos)
    assert expect == actual
