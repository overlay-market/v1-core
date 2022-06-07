from pytest import approx
from decimal import Decimal

from .utils import price_to_tick


def test_notional_with_pnl(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    current_price = 150000000000000000000  # 150
    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 950000000000000000  # 0.95
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.095

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 950000000000000000  # 0.95
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.076

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check current notional is oi * current_price
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 11920000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps and rounding
    assert expect == approx(actual, rel=1.05e-4)

    # check current notional is 2 * oi * entry_price - oi * current_price
    # when short
    is_long = False
    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 3920000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps and rounding
    assert expect == approx(actual, rel=1.05e-4)


def test_notional_with_pnl_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 8000  # 0.8

    current_price = 150000000000000000000  # 150
    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 950000000000000000  # 0.95
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.076

    # inputs for position function
    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check current notional is oi * current_price
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 2980000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps and rounding
    assert expect == approx(actual, rel=1.05e-4)

    # check current notional is 2 * oi * entry_price - oi * current_price
    # when short
    is_long = False
    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 980000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps and rounding
    assert expect == approx(actual, rel=1.05e-4)


def test_notional_with_pnl_when_payoff_greater_than_cap(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 10000  # 1.0

    current_price = 800000000000000000000  # 800
    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 950000000000000000  # 0.95
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.095

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check current notional is oi * current_price
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 60500000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)

    # NOTE: rel tol of 1.05e-4 given tick has precision to 1bps and rounding
    assert expect == approx(actual, rel=1.05e-4)


def test_notional_with_pnl_when_underwater(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 10000  # 1.0

    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 950000000000000000  # 0.95
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.095

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns the debt (floors to debt) when short is underwater
    is_long = False
    current_price = 225000000000000000000  # 225
    expect = debt
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_fraction_remaining_zero(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    fraction_remaining = 0  # 0

    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 950000000000000000  # 0.95
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.095

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns the debt (floors to debt) when short is underwater
    is_long = False
    current_price = 225000000000000000000  # 225
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 0
    actual = position.notionalWithPnl(pos, fraction, oi, oi_shares,
                                      current_price, cap_payoff)
    assert expect == actual
