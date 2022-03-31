def test_oi_shares_current(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 1000000000000000000  # 1

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 10
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_oi_shares_current_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 250000000000000000  # 0.25

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 10
    actual = position.oiSharesCurrent(pos, fraction)
    assert expect == actual


def test_debt(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 1000000000000000000  # 1

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oiShares * fraction
    expect = int(debt * (fraction / 1e18))  # 2
    actual = position.debtCurrent(pos, fraction)
    assert expect == actual


def test_debt_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 250000000000000000  # 0.25

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oiShares * fraction
    expect = int(debt * (fraction / 1e18))  # 2
    actual = position.debtCurrent(pos, fraction)
    assert expect == actual


def test_oi_initial(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 1000000000000000000  # 1

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 2
    actual = position.oiInitial(pos, fraction)
    assert expect == actual


def test_oi_initial_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 250000000000000000  # 0.25

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check oiShares * fraction
    expect = int(oi * (fraction / 1e18))  # 2
    actual = position.oiInitial(pos, fraction)
    assert expect == actual


def test_cost(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 1000000000000000000  # 1

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check cost = notional - debt
    expect = int((notional - debt) * (fraction / 1e18))  # 8
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_cost_when_fraction_less_than_one(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101
    fraction = 250000000000000000  # 0.25

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check cost = oi - debt
    expect = int((notional - debt) * (fraction / 1e18))  # 8
    actual = position.cost(pos, fraction)
    assert expect == actual


def test_exists(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check exists when not liquidated and oi > 0
    expect = True
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_liquidated(position):
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = True
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check exists when not liquidated and oi > 0
    expect = False
    actual = position.exists(pos)
    assert expect == actual


def test_exists_when_oi_zero(position):
    notional = 0  # 0
    debt = 2000000000000000000  # 2
    is_long = True
    liquidated = False
    mid_price = 100000000000000000000  # 100
    entry_price = 101000000000000000000  # 101

    oi = int((notional / mid_price) * 1000000000000000000)  # 0.1
    # NOTE: mid_ratio tests in test_entry_price.py
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    # check exists when not liquidated and oi > 0
    expect = False
    actual = position.exists(pos)
    assert expect == actual
