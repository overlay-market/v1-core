def test_is_underwater(position):
    leverage = 5000000000000000000  # 5x
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2

    tol = 1e-4  # 1 bps

    # check returns True when long is underwater
    is_long = True
    current_price = 80000000000000000000 * (1 - tol)  # 80 * (1-tol)
    expect = True
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns False when long is not underwater
    is_long = True
    current_price = 80000000000000000000 * (1 + tol)  # 80 * (1+tol)
    expect = False
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns True when short is underwater
    is_long = False
    current_price = 120000000000000000000 * (1 + tol)  # 120 * (1+tol)
    expect = True
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns False when short is not underwater
    is_long = False
    current_price = 120000000000000000000 * (1 - tol)  # 120 * (1-tol)
    expect = False
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual


def test_is_underwater_when_oi_zero(position):
    leverage = 5000000000000000000  # 5x
    entry_price = 100000000000000000000  # 100
    current_price = 90000000000000000000  # 90
    oi = 0  # 0
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2

    # check returns True when long oi is zero and has debt
    is_long = True
    expect = True
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns True when short oi is zero and has debt
    is_long = False
    expect = True
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual


def test_is_underwater_when_leverage_one(position):
    leverage = 1000000000000000000  # 1x
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 0  # 0
    cost = 10000000000000000000  # 10

    tol = 1e-4  # 1bps

    # check returns False when long leverage is 1
    is_long = True
    current_price = 75000000000000000000  # 75
    expect = False
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns False when short price moves less than 2x
    is_long = False
    current_price = 200000000000000000000 * (1 - tol)  # 200 * (1-tol)
    expect = False
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual

    # check returns True when short price moves more than 2x
    is_long = False
    current_price = 200000000000000000000 * (1 + tol)  # 200 * (1+tol)
    expect = True
    pos = (leverage, is_long, entry_price, oi, debt, cost)
    actual = position.isUnderwater(pos, oi, oi, current_price)
    assert expect == actual


def test_is_liquidatable(position):
    pass


def test_is_liquidatable_when_oi_zero(position):
    # TODO: should return false always since no oi
    pass


def test_is_liquidatable_when_leverage_one(position):
    # TODO: should return false always since no debt
    pass


def test_liquidation_price(position):
    pass


def test_liquidation_price_when_oi_zero(position):
    # TODO: should return 0 (long) or max int (short) since no oi
    pass


def test_liquidation_price_when_leverage_one(position):
    # TODO: should return 0 (long) or max int (short) since no leverage
    pass
