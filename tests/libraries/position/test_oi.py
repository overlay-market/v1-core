def test_oi_current(position):
    # NOTE: oi = pos.oi_shares
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    fraction = 1000000000000000000  # 1

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # lost 3 from total oi due to funding
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    expect = int((total_oi * oi / total_oi_shares) * (fraction / 1e18))
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual


def test_oi_current_when_fraction_less_than_one(position):
    # NOTE: oi = pos.oi_shares
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    fraction = 250000000000000000  # 0.25

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # lost 3 from total oi due to funding
    total_oi = 12000000000000000000  # 12
    total_oi_shares = 15000000000000000000  # 15

    # check oi is pro-rata shares of total oi
    expect = int((total_oi * oi / total_oi_shares) * (fraction / 1e18))
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual


def test_oi_current_when_total_oi_or_oi_shares_zero(position):
    """
    Tests four possible cases of when oi should return 0

    Cases:
    1. total_oi = 0; oi_shares, total_oi_shares != 0
    2. oi_shares = 0; total_oi, total_oi_shares != 0
    3. oi_shares, total_oi, total_oi_shares = 0
    4. oi_shares, total_oi = 0; total_oi_shares != 0
    """
    # NOTE: oi = pos.oi_shares
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    debt = 2000000000000000000  # 2
    fraction = 1000000000000000000  # 1

    # 1. lost it all due to funding (t -> infty)
    notional = 10000000000000000000  # 10
    total_oi = 0  # 0
    total_oi_shares = 15000000000000000000  # 15
    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    # check oi is zero
    expect = 0
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 2. unwound all of position oi
    notional = 0  # 0
    total_oi = 4000000000000000000  # 4
    total_oi_shares = 5000000000000000000  # 5
    oi = (notional / entry_price) * 1000000000000000000  # 0

    expect = 0
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 3. all oi has been unwound
    notional = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 0  # 0
    oi = (notional / entry_price) * 1000000000000000000  # 0

    expect = 0
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual

    # 4. position has been liquidated
    notional = 0  # 0
    total_oi = 0  # 0
    total_oi_shares = 5000000000000000000  # 5
    liquidated = True
    oi = (notional / entry_price) * 1000000000000000000  # 0

    expect = 0
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.oiCurrent(pos, fraction, total_oi, total_oi_shares)
    assert expect == actual
