def test_notional_initial(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 1000000000000000000  # 1

    # check initial notional is oi * entry_price = notional
    # when long
    is_long = True
    expect = notional
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual

    # check initial notional is oi * entry_price = notional
    # when short
    is_long = False
    expect = notional
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual


def test_notional_initial_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 250000000000000000  # 0.25

    # check initial notional is oi * entry_price = notional
    # when long
    is_long = True
    expect = 2500000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual

    # check initial notional is oi * entry_price = notional
    # when short
    is_long = False
    expect = 2500000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalInitial(pos, fraction)
    assert expect == actual


def test_notional_with_pnl(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check current notional is oi * current_price
    # when long
    is_long = True
    expect = 15000000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual

    # check current notional is 2 * oi * entry_price - oi * current_price
    # when short
    is_long = False
    expect = 5000000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi * current_price
    # when long
    is_long = True
    expect = 3750000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual

    # check notional is 2 * oi * entry_price - oi * current_price
    # when short
    is_long = False
    expect = 1250000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_payoff_greater_than_cap(position):
    entry_price = 100000000000000000000  # 100
    current_price = 800000000000000000000  # 800
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional is oi * entry_price * (1 + cap_payoff)
    # when long
    is_long = True
    expect = 60000000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_underwater(position):
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns the debt (floors to debt) when short is underwater
    is_long = False
    current_price = 225000000000000000000  # 225
    expect = debt
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual


def test_notional_with_pnl_when_oi_zero(position):
    current_price = 75000000000000000000  # 75
    entry_price = 100000000000000000000  # 100
    notional = 0  # 0
    debt = 2000000000000000000  # 2
    liquidated = False

    oi = (notional / entry_price) * 1000000000000000000  # 0
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check notional returns debt when oi is zero and is long
    is_long = True
    expect = debt
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual

    # check notional returns the debt when oi is zero and is short
    is_long = False
    expect = debt
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.notionalWithPnl(pos, fraction, oi, oi, current_price,
                                      cap_payoff)
    assert expect == actual
