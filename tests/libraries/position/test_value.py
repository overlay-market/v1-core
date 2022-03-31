def test_value(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * current_price - debt
    # when long
    is_long = True
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 13000000000000000000  # 13
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 3000000000000000000  # 3
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_entry_not_equal_to_mid(position):
    mid_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * current_price - debt
    # when long
    is_long = True
    entry_price = 102500000000000000000  # 102.5
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 12750000000000000000  # 12.75
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    entry_price = 97500000000000000000  # 97.5
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 2750000000000000000  # 2.75
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * current_price - debt
    # when long
    is_long = True
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 3250000000000000000
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value is 2 * oi * entry_price - debt - oi * current_price
    # when short
    is_long = False
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 750000000000000000
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_payoff_greater_than_cap(position):
    entry_price = 100000000000000000000  # 100
    current_price = 800000000000000000000  # 800
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value is oi * entry_price * (1 + cap_payoff) - debt
    # when long
    is_long = True
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 58000000000000000000
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_underwater(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    liquidated = False

    oi = int((notional / entry_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value returns zero when long is underwater
    is_long = True
    current_price = 75000000000000000000  # 75
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value returns zero when short is underwater
    is_long = False
    current_price = 125000000000000000000  # 125
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual


def test_value_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    entry_price = 100000000000000000000  # 100
    notional = 0  # 0
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = int((notional / entry_price) * 1000000000000000000)  # 0
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check value returns zero when oi is zero and is long
    is_long = True
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual

    # check value returns zero when oi is zero and is short
    is_long = False
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, entry_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 0
    actual = position.value(pos, fraction, oi, oi, current_price, cap_payoff)
    assert expect == actual
