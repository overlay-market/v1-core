from pytest import approx
from brownie.test import given, strategy
from decimal import Decimal

from .utils import price_to_tick


@given(mid_price=strategy('decimal', min_value='2e-18'))
def test_mid_price_at_entry(position, mid_price):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 9000  # 0.9

    mid_price = int(mid_price * Decimal(1e18))
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = mid_price
    actual = int(position.midPriceAtEntry(pos))
    assert expect == approx(actual, rel=1e-4)


@given(entry_price=strategy('decimal', min_value='2e-18'))
def test_entry_price(position, entry_price):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 9000  # 0.9

    mid_price = 100000000000000000000  # 100
    entry_price = int(entry_price * Decimal(1e18))

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = entry_price
    actual = int(position.entryPrice(pos))
    assert expect == approx(actual, rel=1e-4)
