def test_value(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    cost = 8000000000000000000  # 8

    # check value is oi - debt + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 13000000000000000000
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.value(pos, oi, oi, current_price)
    assert expect == actual

    # check value is oi - debt - oi * (current_price/entry_price - 1)
    # when short
    is_long = False
    expect = 3000000000000000000
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.value(pos, oi, oi, current_price)
    assert expect == actual


def test_value_when_underwater(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2

    # check value returns zero when long is underwater
    is_long = True
    current_price = 75000000000000000000  # 75
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.value(pos, oi, oi, current_price)
    assert expect == actual

    # check value returns zero when short is underwater
    is_long = False
    current_price = 125000000000000000000  # 125
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.value(pos, oi, oi, current_price)
    assert expect == actual


def test_value_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    entry_price = 100000000000000000000  # 100
    oi = 0  # 0
    cost = 8000000000000000000  # 8
    debt = 2000000000000000000  # 2

    # check value returns zero when oi is zero and is long
    is_long = True
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.value(pos, oi, oi, current_price)
    assert expect == actual

    # check value returns zero when oi is zero and is short
    is_long = False
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.value(pos, oi, oi, current_price)
    assert expect == actual


def test_notional(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    cost = 8000000000000000000  # 8

    # check notional is oi + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 15000000000000000000
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.notional(pos, oi, oi, current_price)
    assert expect == actual

    # check value is oi - oi * (current_price/entry_price - 1)
    # when short
    is_long = False
    expect = 5000000000000000000
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.notional(pos, oi, oi, current_price)
    assert expect == actual


def test_notional_when_underwater(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    cost = 2000000000000000000  # 2

    # check notional returns zero when short is underwater
    is_long = False
    current_price = 225000000000000000000  # 225
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.notional(pos, oi, oi, current_price)
    assert expect == actual


def test_notional_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    entry_price = 100000000000000000000  # 100
    oi = 0  # 0
    cost = 8000000000000000000  # 8
    debt = 2000000000000000000  # 2

    # check notional returns zero when oi is zero and is long
    is_long = True
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.notional(pos, oi, oi, current_price)
    assert expect == actual

    # check notional returns zero when oi is zero and is short
    is_long = False
    expect = 0
    pos = (entry_price, oi, debt, cost, is_long)
    actual = position.notional(pos, oi, oi, current_price)
    assert expect == actual
