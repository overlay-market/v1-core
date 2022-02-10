def test_value(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value is oi - debt + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 13000000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value is oi - debt - oi * (current_price/entry_price - 1)
    # when short
    is_long = False
    expect = 3000000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check value is oi - debt + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 3250000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value is oi - debt - oi * (current_price/entry_price - 1)
    # when short
    is_long = False
    expect = 750000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_payoff_greater_than_cap(position):
    entry_price = 100000000000000000000  # 100
    current_price = 800000000000000000000  # 800
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value is oi - debt + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 58000000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_underwater(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value returns zero when long is underwater
    is_long = True
    current_price = 75000000000000000000  # 75
    expect = 0
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value returns zero when short is underwater
    is_long = False
    current_price = 125000000000000000000  # 125
    expect = 0
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    entry_price = 100000000000000000000  # 100
    oi = 0  # 0
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value returns zero when oi is zero and is long
    is_long = True
    expect = 0
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value returns zero when oi is zero and is short
    is_long = False
    expect = 0
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual
