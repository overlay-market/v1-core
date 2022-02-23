def test_oi_shares_current(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 10
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_oi_shares_current_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 10
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_debt(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oiShares * fraction
    expect = int(debt * (fraction / 1e18))  # 2
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.debtCurrent(pos, fraction)
    assert expect == actual


def test_debt_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oiShares * fraction
    expect = int(debt * (fraction / 1e18))  # 2
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.debtCurrent(pos, fraction)
    assert expect == actual


def test_oi_initial(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 2
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiInitial(pos, fraction)
    assert expect == actual


def test_oi_initial_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 2
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiInitial(pos, fraction)
    assert expect == actual


def test_cost(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check cost = notional - debt
    expect = int((notional - debt) * (fraction / 1e18))  # 8
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_cost_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check cost = oi - debt
    expect = int((notional - debt) * (fraction / 1e18))  # 8
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_exists(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check exists when not liquidated and oi > 0
    expect = True
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_liquidated(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = True
    entry_price = 100000000000000000000  # 100

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check exists when not liquidated and oi > 0
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_oi_zero(position):
    notional = 0  # 0
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check exists when not liquidated and oi > 0
    expect = False
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.exists(pos)
    assert expect == actual
