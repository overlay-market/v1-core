def test_notional(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 15000000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual

    # check value is oi - oi * (current_price/entry_price - 1)
    # when short
    is_long = False
    expect = 5000000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual


def test_notional_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 3750000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual

    # check value is oi - oi * (current_price/entry_price - 1)
    # when short
    is_long = False
    expect = 1250000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual


def test_notional_when_payoff_greater_than_cap(position):
    entry_price = 100000000000000000000  # 100
    current_price = 800000000000000000000  # 800
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi + oi * (current_price/entry_price - 1)
    # when long
    is_long = True
    expect = 60000000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual


def test_notional_when_underwater(position):
    entry_price = 100000000000000000000  # 100
    oi = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns the debt (floors to debt) when short is underwater
    is_long = False
    current_price = 225000000000000000000  # 225
    expect = debt
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual


def test_notional_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    entry_price = 100000000000000000000  # 100
    oi = 0  # 0
    debt = 2000000000000000000  # 2
    liquidated = False

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns debt when oi is zero and is long
    is_long = True
    expect = debt
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual

    # check notional returns the debt when oi is zero and is short
    is_long = False
    expect = debt
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.notional(pos, fraction, oi, oi, current_price,
                               cap_payoff)
    assert expect == actual
