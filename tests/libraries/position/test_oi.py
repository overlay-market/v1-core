def test_initial_oi(position):
    leverage = 1250000000000000000  # 1.25x
    is_long = True
    entry_price = 100000000000000000000  # 100
    oi_shares = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    cost = 8000000000000000000  # 8

    # check initial oi is debt + cost
    expect = 10000000000000000000
    pos = (leverage, is_long, entry_price, oi_shares, debt, cost)
    actual = position.initialOi(pos)

    assert expect == actual


def test_oi(position):
    leverage = 1250000000000000000  # 1.25x
    is_long = True
    entry_price = 100000000000000000000  # 100
    oi_shares = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    cost = 8000000000000000000  # 8

    # lost 3 from total oi due to funding
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    expect = total_oi * oi_shares / total_oi_shares
    pos = (leverage, is_long, entry_price, oi_shares, debt, cost)
    actual = position.oi(pos, total_oi, total_oi_shares)

    assert expect == actual


def test_oi_when_total_oi_or_oi_shares_zero(position):
    """
    Tests four possible cases of when oi should return 0

    Cases:
    1. total_oi = 0; oi_shares, total_oi_shares != 0
    2. oi_shares = 0; total_oi, total_oi_shares != 0
    3. oi_shares, total_oi, total_oi_shares = 0
    4. oi_shares, total_oi = 0; total_oi_shares != 0
    """
    leverage = 1250000000000000000  # 1.25x
    is_long = True
    entry_price = 100000000000000000000  # 100
    debt = 2000000000000000000  # 2
    cost = 8000000000000000000  # 8

    # 1. lost it all due to funding (t -> infty)
    oi_shares = 10000000000000000000  # 10
    total_oi = 0  # 0
    total_oi_shares = 15000000000000000000  # 15

    # check oi is zero
    expect = 0
    pos = (leverage, is_long, entry_price, oi_shares, debt, cost)
    actual = position.oi(pos, total_oi, total_oi_shares)
    assert expect == actual

    # 2. unwound all position's shares of oi
    oi_shares = 0  # 0
    total_oi = 4000000000000000000  # 4
    total_oi_shares = 5000000000000000000  # 5

    expect = 0
    pos = (leverage, is_long, entry_price, oi_shares, debt, cost)
    actual = position.oi(pos, total_oi, total_oi_shares)
    assert expect == actual

    # 3. all oi has been unwound
    oi_shares = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 0  # 0

    expect = 0
    pos = (leverage, is_long, entry_price, oi_shares, debt, cost)
    actual = position.oi(pos, total_oi, total_oi_shares)
    assert expect == actual

    # 4. position has been liquidated
    oi_shares = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 5000000000000000000  # 5

    expect = 0
    pos = (leverage, is_long, entry_price, oi_shares, debt, cost)
    actual = position.oi(pos, total_oi, total_oi_shares)
    assert expect == actual
