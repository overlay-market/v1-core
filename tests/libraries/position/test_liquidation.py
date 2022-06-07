from decimal import Decimal

from .utils import price_to_tick


def test_liquidatable(position):
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    fraction_remaining = 8000  # 0.8
    liquidated = False

    entry_price = 100000000000000000000  # 100
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick

    oi = int(Decimal(notional) / Decimal(entry_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    # inputs for position function
    cap_payoff = 5000000000000000000  # 5

    tol = 1e-4  # 1 bps

    # liquidatable when:
    # position.value * (1-liq_fee_rate) < maintenance * initial_notional
    # check returns True when long is liquidatable
    is_long = True
    current_price = 90526315789473677312 * (1 - tol)  # ~ 90.5263 * (1-tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = True
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when long is not liquidatable
    is_long = True
    current_price = 90526315789473677312 * (1 + tol)  # ~ 90.5263 * (1+tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when short is liquidatable
    is_long = False
    current_price = 109473684210526322688 * (1 + tol)  # ~ 109.4737 * (1+tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = True
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short is not liquidatable
    is_long = False
    current_price = 109473684210526322688 * (1 - tol)  # ~ 109.4737 * (1-tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_entry_not_equal_to_mid(position):
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    fraction_remaining = 8000  # 0.8
    liquidated = False

    mid_price = 100000000000000000000  # 100
    mid_tick = price_to_tick(mid_price)

    oi = int(Decimal(notional) / Decimal(mid_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    # inputs for position function
    cap_payoff = 5000000000000000000  # 5

    tol = 1e-4  # 1 bps

    # liquidatable when position.value < maintenance * initial_notional
    # check returns True when long is liquidatable
    is_long = True
    current_price = 90527315789473693696 * (1 - tol)  # ~ 90.5273 * (1-tol)
    entry_price = 100001000000000000000  # 100.001
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = True
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when long is not liquidatable
    is_long = True
    current_price = 90527315789473693696 * (1 + tol)  # ~ 90.5273 * (1+tol)
    entry_price = 100001000000000000000  # 100.001
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when short is liquidatable
    is_long = False
    current_price = 109472684210526306304 * (1 + tol)  # ~ 109.4727 * (1+tol)
    entry_price = 99999000000000000000  # 99.999
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = True
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short is not liquidatable
    is_long = False
    current_price = 109472684210526306304 * (1 - tol)  # ~ 109.4727 * (1-tol)
    entry_price = 99999000000000000000  # 99.999
    entry_tick = price_to_tick(entry_price)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_oi_zero(position):
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    fraction_remaining = 0  # 0
    liquidated = False

    entry_price = 100000000000000000000  # 100
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick
    current_price = 90000000000000000000  # 90

    # inputs for position function
    cap_payoff = 5000000000000000000  # 5

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # check returns False when long oi is zero
    is_long = True
    expect = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short oi is zero
    is_long = False
    expect = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_liquidated(position):
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    fraction_remaining = 0  # 0
    liquidated = True
    cap_payoff = 5000000000000000000  # 5

    entry_price = 100000000000000000000  # 100
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick
    current_price = 90000000000000000000  # 90

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.08

    # check returns False when long oi has been liquidated
    is_long = True
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short oi has been liquidated
    is_long = False
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_leverage_one(position):
    notional = 10000000000000000000  # 10
    debt = 0  # 0
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    liquidated = False
    fraction_remaining = 8000  # 0.8

    cap_payoff = 5000000000000000000  # 5

    entry_price = 100000000000000000000  # 100
    entry_tick = price_to_tick(entry_price)
    mid_tick = entry_tick

    oi = int(Decimal(notional) / Decimal(entry_price) * Decimal(1e18)
             * Decimal(fraction_remaining) / Decimal(1e4))  # 0.08
    shares_to_oi_ratio = 800000000000000000  # 0.8
    oi_shares = int(Decimal(oi) * Decimal(shares_to_oi_ratio)
                    / Decimal(1e18))  # 0.064

    tol = 1e-4  # 1bps

    # check returns False when long price moves less than maintenance require
    is_long = True
    current_price = 10526315789473685504 * (1 + tol)  # ~ 10.5263 * (1+tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when long price moves more than maintenance require
    is_long = True
    current_price = 10526315789473685504 * (1 - tol)  # ~ 10.5263 * (1-tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = True
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short price moves less than maintenance require
    is_long = False
    current_price = 189473684210526289920 * (1 - tol)  # ~ 189.4736 * (1-tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = False
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when short price moves more than maintenance require
    is_long = False
    current_price = 189473684210526289920 * (1 + tol)  # ~ 189.4736 * (1+tol)
    pos = (notional, debt, mid_tick, entry_tick, is_long,
           liquidated, oi_shares, fraction_remaining)

    expect = True
    actual = position.liquidatable(pos, oi, oi_shares, current_price,
                                   cap_payoff, maintenance, liq_fee_rate)
    assert expect == actual
