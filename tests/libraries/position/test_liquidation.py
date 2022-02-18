def test_liquidatable(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    tol = 1e-4  # 1 bps

    # liquidatable when position.value < maintenance * initial_notional
    # check returns True when long is liquidatable
    is_long = True
    current_price = 90000000000000000000 * (1 - tol)  # 90 * (1-tol)
    expect = True
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns False when long is not liquidatable
    is_long = True
    current_price = 90000000000000000000 * (1 + tol)  # 90 * (1+tol)
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns True when short is liquidatable
    is_long = False
    current_price = 110000000000000000000 * (1 + tol)  # 110 * (1+tol)
    expect = True
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns False when short is not liquidatable
    is_long = False
    current_price = 110000000000000000000 * (1 - tol)  # 110 * (1-tol)
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual


def test_liquidatable_when_oi_zero(position):
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    notional = 0  # 0
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    oi = (notional / entry_price) * 1000000000000000000  # 0

    # check returns False when long oi is zero
    is_long = True
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns False when short oi is zero
    is_long = False
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual


def test_liquidatable_when_liquidated(position):
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    notional = 0  # 0
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liquidated = True
    cap_payoff = 5000000000000000000  # 5

    oi = (notional / entry_price) * 1000000000000000000  # 0

    # check returns False when long oi is zero
    is_long = True
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns False when short oi is zero
    is_long = False
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual


def test_liquidatable_when_leverage_one(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 0  # 0
    maintenance = 100000000000000000  # 10%
    liquidated = False
    cap_payoff = 5000000000000000000  # 5

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    tol = 1e-4  # 1bps

    # check returns False when long price moves less than maintenance require
    is_long = True
    current_price = 10000000000000000000 * (1 + tol)  # 10 * (1+tol)
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns True when long price moves more than maintenance require
    is_long = True
    current_price = 10000000000000000000 * (1 - tol)  # 10 * (1-tol)
    expect = True
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns False when short price moves less than maintenance require
    is_long = False
    current_price = 190000000000000000000 * (1 - tol)  # 190 * (1-tol)
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual

    # check returns True when short price moves more than maintenance require
    is_long = False
    current_price = 190000000000000000000 * (1 + tol)  # 190 * (1+tol)
    expect = True
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidatable(pos, oi, oi, current_price, cap_payoff,
                                   maintenance)
    assert expect == actual


def test_liquidation_price(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # liquidatable price occurs when position.value = maintenance * initial_oi
    # check returns correct liquidation price for long
    is_long = True
    expect = 90000000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidationPrice(pos, oi, oi, maintenance)
    assert expect == actual

    # check returns correct liquidation price for short
    is_long = False
    expect = 110000000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price)
    actual = position.liquidationPrice(pos, oi, oi, maintenance)
    assert expect == actual


def test_liquidation_price_when_oi_zero(position):
    entry_price = 100000000000000000000  # 100
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liquidated = False
    is_long = True

    # check liqPrice is zero when posOiInitial is zero
    notional = 0
    total_oi = 100
    pos = (notional, debt, is_long, liquidated, entry_price)

    expect = 0
    actual = position.liquidationPrice(pos, total_oi, total_oi, maintenance)
    assert expect == actual

    # check liqPrice is zero when posOiCurrent is zero
    notional = 100
    total_oi = 0
    pos = (notional, debt, is_long, liquidated, entry_price)

    expect = 0
    actual = position.liquidationPrice(pos, total_oi, total_oi, maintenance)
    assert expect == actual


def test_liquidation_price_when_liquidated_is_true(position):
    entry_price = 100000000000000000000  # 100
    debt = 8000000000000000000  # 8
    maintenance = 100000000000000000  # 10%
    liquidated = True
    is_long = True

    # check liqPrice is zero when posOiInitial is zero
    notional = 100
    total_oi = 100
    pos = (notional, debt, is_long, liquidated, entry_price)

    expect = 0
    actual = position.liquidationPrice(pos, total_oi, total_oi, maintenance)
    assert expect == actual
