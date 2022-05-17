from brownie import reverts
from brownie.test import given, strategy
from decimal import Decimal

from .utils import price_to_tick


@given(fraction_remaining=strategy('uint16', max_value="10000"))
def test_get_fraction_remaining(position, fraction_remaining):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False

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

    # check get fraction remaining converts to uint256 FixedPoint
    # 18 decimal fraction
    expect = int(Decimal(fraction_remaining) * Decimal(1e14))
    actual = position.getFractionRemaining(pos)
    assert expect == actual


@given(
    fraction_remaining=strategy('uint16', max_value="10000"),
    fraction_removed=strategy('uint16', max_value="10000"))
def test_updated_fraction_remaining(position, fraction_remaining,
                                    fraction_removed):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False

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

    # calculate updated fraction remaining
    fraction_removed_256 = fraction_removed * Decimal(1e14)
    fraction_remaining_256 = fraction_remaining * Decimal(1e14)
    updated_fraction_remaining_256 = fraction_remaining_256 * \
        (Decimal(1e18) - fraction_removed_256) / Decimal(1e18)
    updated_fraction_remaining = int(
        updated_fraction_remaining_256 / Decimal(1e14))

    # check updated fraction remaining once remove from remaining
    expect = updated_fraction_remaining
    actual = position.updatedFractionRemaining(pos, fraction_removed_256)
    assert expect == actual


def test_updated_fraction_remaining_reverts_when_gt_max(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 9000  # 0.9

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

    # check fails when greater than ONE
    fraction_removed = 1000000000000000001  # 1 greater than ONE (18 decimals)
    with reverts("OVLV1:fraction>max"):
        position.updatedFractionRemaining(pos, fraction_removed)

    # check succeeds when equal to ONE
    fraction_removed = 1000000000000000000
    expect = 0
    actual = position.updatedFractionRemaining(pos, fraction_removed)
    assert expect == actual
