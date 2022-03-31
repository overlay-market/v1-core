def test_notional_initial(position):
    mid_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1

    # check initial notional is oi * entry_price = notional
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = notional
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual

    # check initial notional is oi * entry_price = notional
    # when short
    is_long = False
    entry_price = 99000000000000000000  # 99
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = notional
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual


def test_notional_initial_when_fraction_less_than_one(position):
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    fraction = 250000000000000000  # 0.25

    # check initial notional is oi * entry_price = notional
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 2500000000000000000
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual

    # check initial notional is oi * entry_price = notional
    # when short
    is_long = False
    entry_price = 99000000000000000000  # 99
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 2500000000000000000
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual


def test_notional_with_pnl(position):
    mid_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check current notional is oi * current_price
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 14900000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual

    # check current notional is 2 * oi * entry_price - oi * current_price
    # when short
    is_long = False
    entry_price = 99000000000000000000  # 99
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 4900000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_fraction_less_than_one(position):
    mid_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi * current_price
    # when long
    is_long = True
    entry_price = 101000000000000000000  # 101
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 3725000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual

    # check notional is 2 * oi * entry_price - oi * current_price
    # when short
    is_long = False
    entry_price = 99000000000000000000  # 99
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = 1225000000000000000
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_payoff_greater_than_cap(position):
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    current_price = 800000000000000000000  # 800
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi * entry_price * (1 + cap_payoff)
    # when long
    is_long = True
    expect = 60500000000000000000
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_underwater(position):
    mid_price = 100000000000000000000  # 100
    entry_price = 99000000000000000000  # 99
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns the debt (floors to debt) when short is underwater
    is_long = False
    current_price = 225000000000000000000  # 225
    expect = debt
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    mid_price = 100000000000000000000  # 100
    notional = 0  # 0
    debt = 2000000000000000000  # 2
    liquidated = False

    # NOTE: mid_ratio tests in test_entry_price.py
    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns debt when oi is zero and is long
    is_long = True
    entry_price = 101000000000000000000  # 101
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = debt
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual

    # check notional returns the debt when oi is zero and is short
    is_long = False
    entry_price = 99000000000000000000  # 99
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = debt
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual
