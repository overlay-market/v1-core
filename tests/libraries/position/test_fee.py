from pytest import approx
from decimal import Decimal

from .utils import price_to_tick


def test_trading_fee(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    fraction_remaining = 10000  # 1.0
    trading_fee_rate = 750000000000000  # 0.00075

    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150

    # set mid to entry for this test
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # inputs for position function
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notionalWithPnl * fee_rate
    is_long = True
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 11250000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)

    # check trading fee is notionalWithPnl * fee_rate
    is_long = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 3750000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)

    # check trading fee is notional * fee_rate when 0 price change
    is_long = True
    current_price = entry_price
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 7500000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)

    # check trading fee is notional * fee_rate when 0 price change
    is_long = False
    current_price = entry_price
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 7500000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)


def test_trading_fee_when_entry_not_equal_to_mid(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    fraction_remaining = 10000  # 1.0
    trading_fee_rate = 750000000000000  # 0.00075

    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)
    current_price = 150000000000000000000  # 150

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # position fn inputs
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notionalWithPnl * fee_rate
    is_long = True
    entry_price = 101000000000000000000  # 101
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 11175000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1.05e-4)

    # check trading fee is notionalWithPnl * fee_rate
    is_long = False
    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 3675000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1.05e-4)

    # check trading fee is notional * fee_rate when 0 price change
    is_long = True
    entry_price = 101000000000000000000  # 101
    entry_tick = price_to_tick(entry_price)
    current_price = entry_price
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 7500000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1.05e-4)

    # check trading fee is notional * fee_rate when 0 price change
    is_long = False
    entry_price = 99000000000000000000  # 99
    entry_tick = price_to_tick(entry_price)
    current_price = entry_price
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 7500000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1.05e-4)


def test_trading_fee_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    fraction_remaining = 8000  # 0.8
    trading_fee_rate = 750000000000000  # 0.00075

    entry_price = 100000000000000000000  # 100
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick
    current_price = 150000000000000000000  # 150

    # oi and oi shares
    oi = int(Decimal(notional) / Decimal(entry_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(
        Decimal(oi) * (Decimal(shares_to_oi_ratio) / Decimal(1e18)))  # 0.064

    # position fn inputs
    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notionalWithPnl * fee_rate
    is_long = True
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 2250000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)

    # check trading fee is notional * fee_rate
    is_long = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 750000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)


def test_trading_fee_when_payoff_greater_than_cap(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    fraction_remaining = 10000  # 1.0
    trading_fee_rate = 750000000000000  # 0.00075

    # prices
    entry_price = 100000000000000000000  # 100
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick
    current_price = 800000000000000000000  # 800

    # oi and oi shares
    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # pos fn inputs
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notionalWithPnl * fee_rate
    is_long = True
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = 45000000000000000
    actual = position.tradingFee(pos, fraction, oi, oi_shares, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == approx(actual, rel=1e-4)
