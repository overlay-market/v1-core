def test_oi_shares_current(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 10
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_oi_shares_current_when_fraction_less_than_one(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 10
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_debt_current(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    # check oiShares * fraction
    expect = int(debt * (fraction / 1e18))  # 2
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.debtCurrent(pos, fraction)
    assert expect == actual


def test_debt_current_when_fraction_less_than_one(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    # check oiShares * fraction
    expect = int(debt * (fraction / 1e18))  # 2
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.debtCurrent(pos, fraction)
    assert expect == actual


def test_oi_initial(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 2
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.oiInitial(pos, fraction)
    assert expect == actual


def test_oi_initial_when_fraction_less_than_one(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 2
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.oiInitial(pos, fraction)
    assert expect == actual


def test_cost(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 1000000000000000000  # 1

    # check cost = oi - debt
    expect = int((oi - debt) * (fraction / 1e18))  # 8
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_cost_when_fraction_less_than_one(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    fraction = 250000000000000000  # 0.25

    # check cost = oi - debt
    expect = int((oi - debt) * (fraction / 1e18))  # 8
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_exists(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100

    # check exists when not liquidated and oi > 0
    expect = True
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_liquidated(position):
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = True
    entry_price = 100000000000000000000  # 100

    # check exists when not liquidated and oi > 0
    expect = False
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_oi_zero(position):
    oi = 0  # 0
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100

    # check exists when not liquidated and oi > 0
    expect = False
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.exists(pos)
    assert expect == actual
