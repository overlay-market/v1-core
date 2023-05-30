from decimal import Decimal

from .utils import get_position_key, price_to_tick


def test_positions_setter(position, alice):
    owner = alice
    id = 0

    is_long = True
    liquidated = False

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    fraction_remaining = 10000  # 1 (4 decimal places for uint16)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long, liquidated,
           oi_shares, fraction_remaining)
    position.set(owner, id, pos)

    # pos key
    pos_key = get_position_key(alice.address, id)

    # check position was added to positions mapping
    expect = pos
    actual = position.positions(pos_key)
    assert expect == actual


def test_positions_getter(position, bob):
    owner = bob
    id = 1

    # add the position first
    is_long = True
    liquidated = False

    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 100

    mid_tick = price_to_tick(mid_price)
    entry_tick = price_to_tick(entry_price)

    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    fraction_remaining = 10000  # 1 (4 decimal places for uint16)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    pos = (notional, debt, mid_tick, entry_tick, is_long, liquidated,
           oi_shares, fraction_remaining)
    position.set(owner, id, pos)

    # check retrieved position is expected
    expect = pos
    actual = position.get(bob, id)
    assert expect == actual
