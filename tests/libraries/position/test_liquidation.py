def test_is_underwater(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2

    tol = 1e-4  # 1 bps

    # check returns True when long is underwater
    is_long = True
    current_price = 80000000000000000000 * (1 - tol)  # 80 * (1-tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns False when long is not underwater
    is_long = True
    current_price = 80000000000000000000 * (1 + tol)  # 80 * (1+tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns True when short is underwater
    is_long = False
    current_price = 120000000000000000000 * (1 + tol)  # 120 * (1+tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns False when short is not underwater
    is_long = False
    current_price = 120000000000000000000 * (1 - tol)  # 120 * (1-tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual


def test_is_underwater_when_oi_zero(position):
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    oi = 0  # 0
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2

    # check returns True when long oi is zero and has debt
    is_long = True
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns True when short oi is zero and has debt
    is_long = False
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual


def test_is_underwater_when_leverage_one(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 0  # 0
    cost = 10000000000000000000  # 10

    tol = 1e-4  # 1bps

    # check returns False when long leverage is 1
    is_long = True
    current_price = 75000000000000000000  # 75
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns False when short price moves less than 2x
    is_long = False
    current_price = 200000000000000000000 * (1 - tol)  # 200 * (1-tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns True when short price moves more than 2x
    is_long = False
    current_price = 200000000000000000000 * (1 + tol)  # 200 * (1+tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual


def test_is_liquidatable(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2
    maintenance = 100000000000000000  # 10%

    tol = 1e-4  # 1 bps

    # liquidatable when position.value < maintenance * initial_oi
    # check returns True when long is liquidatable
    is_long = True
    current_price = 90000000000000000000 * (1 - tol)  # 90 * (1-tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns False when long is not liquidatable
    is_long = True
    current_price = 90000000000000000000 * (1 + tol)  # 90 * (1+tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns True when short is liquidatable
    is_long = False
    current_price = 110000000000000000000 * (1 + tol)  # 110 * (1+tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns False when short is not liquidatable
    is_long = False
    current_price = 110000000000000000000 * (1 - tol)  # 110 * (1-tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual


def test_is_liquidatable_when_oi_zero(position):
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    oi = 0  # 0
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2
    maintenance = 100000000000000000  # 10%

    # check returns True when long oi is zero
    is_long = True
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns True when short oi is zero
    is_long = False
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual


def test_is_liquidatable_when_leverage_one(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 0  # 0
    cost = 10000000000000000000  # 10
    maintenance = 100000000000000000  # 10%

    tol = 1e-4  # 1bps

    # check returns False when long price moves less than maintenance require
    is_long = True
    current_price = 10000000000000000000 * (1 + tol)  # 10 * (1+tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns True when long price moves more than maintenance require
    is_long = True
    current_price = 10000000000000000000 * (1 - tol)  # 10 * (1-tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns False when short price moves less than maintenance require
    is_long = False
    current_price = 190000000000000000000 * (1 - tol)  # 190 * (1-tol)
    expect = False
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual

    # check returns True when short price moves more than maintenance require
    is_long = False
    current_price = 190000000000000000000 * (1 + tol)  # 190 * (1+tol)
    expect = True
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.isLiquidatable(pos, oi, oi, current_price, maintenance)
    assert expect == actual


def test_liquidation_price(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2
    maintenance = 100000000000000000  # 10%

    # liquidatable price occurs when position.value = maintenance * initial_oi
    # check returns correct liquidation price for long
    is_long = True
    expect = 90000000000000000000
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.liquidationPrice(pos, oi, oi, maintenance)
    assert expect == actual

    # check returns correct liquidation price for short
    is_long = False
    expect = 110000000000000000000
    pos = (oi, cost, debt, is_long, entry_price)
    actual = position.liquidationPrice(pos, oi, oi, maintenance)
    assert expect == actual


# TODO: once decide what to return when oi = 0
# def test_liquidation_price_when_oi_zero(position):
#    pass
