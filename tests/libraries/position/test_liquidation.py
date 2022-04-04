def test_liquidatable(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)

    tol = 1e-4  # 1 bps

    # liquidatable when:
    # position.value * (1-liq_fee_rate) < maintenance * initial_notional
    # check returns True when long is liquidatable
    is_long = True
    current_price = 90526315789473677312 * (1 - tol)  # ~ 90.5263 * (1-tol)
    expect = True
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when long is not liquidatable
    is_long = True
    current_price = 90526315789473677312 * (1 + tol)  # ~ 90.5263 * (1+tol)
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when short is liquidatable
    is_long = False
    current_price = 109473684210526322688 * (1 + tol)  # ~ 109.4737 * (1+tol)
    expect = True
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short is not liquidatable
    is_long = False
    current_price = 109473684210526322688 * (1 - tol)  # ~ 109.4737 * (1-tol)
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_entry_not_equal_to_mid(position):
    mid_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    tol = 1e-4  # 1 bps

    # liquidatable when position.value < maintenance * initial_notional
    # check returns True when long is liquidatable
    is_long = True
    current_price = 90527315789473693696 * (1 - tol)  # ~ 90.5273 * (1-tol)
    # NOTE: mid_ratio tests in test_entry_price.py
    entry_price = 100001000000000000000  # 100.001
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)

    expect = True
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when long is not liquidatable
    is_long = True
    current_price = 90527315789473693696 * (1 + tol)  # ~ 90.5273 * (1+tol)
    # NOTE: mid_ratio tests in test_entry_price.py
    entry_price = 100001000000000000000  # 100.001
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)

    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when short is liquidatable
    is_long = False
    current_price = 109472684210526306304 * (1 + tol)  # ~ 109.4727 * (1+tol)
    # NOTE: mid_ratio tests in test_entry_price.py
    entry_price = 99999000000000000000  # 99.999
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    expect = True
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short is not liquidatable
    is_long = False
    current_price = 109472684210526306304 * (1 - tol)  # ~ 109.4727 * (1-tol)
    # NOTE: mid_ratio tests in test_entry_price.py
    entry_price = 99999000000000000000  # 99.999
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_oi_zero(position):
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    notional = 0  # 0
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)

    # check returns False when long oi is zero
    is_long = True
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short oi is zero
    is_long = False
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_liquidated(position):
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    notional = 0  # 0
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    liquidated = True
    cap_payoff = 5000000000000000000  # 5

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)

    # check returns False when long oi is zero
    is_long = True
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short oi is zero
    is_long = False
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual


def test_liquidatable_when_leverage_one(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 0  # 0
    maintenance = 100000000000000000  # 10%
    liq_fee_rate = 50000000000000000  # 5%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)

    tol = 1e-4  # 1bps

    # check returns False when long price moves less than maintenance require
    is_long = True
    current_price = 10526315789473685504 * (1 + tol)  # ~ 10.5263 * (1+tol)
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when long price moves more than maintenance require
    is_long = True
    current_price = 10526315789473685504 * (1 - tol)  # ~ 10.5263 * (1-tol)
    expect = True
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns False when short price moves less than maintenance require
    is_long = False
    current_price = 189473684210526289920 * (1 - tol)  # ~ 189.4736 * (1-tol)
    expect = False
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual

    # check returns True when short price moves more than maintenance require
    is_long = False
    current_price = 189473684210526289920 * (1 + tol)  # ~ 189.4736 * (1+tol)
    expect = True
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance, liq_fee_rate)
    assert expect == actual
