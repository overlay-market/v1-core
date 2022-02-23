def test_trading_fee(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    trading_fee_rate = 750000000000000

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notional * fee_rate
    is_long = True
    expect = 11250000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is notional * fee_rate
    is_long = False
    expect = 3750000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is notional * fee_rate when 0 price change
    is_long = True
    current_price = entry_price
    expect = 7500000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is notional * fee_rate when 0 price change
    is_long = False
    current_price = entry_price
    expect = 7500000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual


def test_trading_fee_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    trading_fee_rate = 750000000000000

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notional * fee_rate
    is_long = True
    expect = 2812500000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is notional * fee_rate
    is_long = False
    expect = 937500000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual


def test_trading_fee_when_payoff_greater_than_cap(position):
    entry_price = 100000000000000000000  # 100
    current_price = 800000000000000000000  # 800
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    trading_fee_rate = 750000000000000

    oi = (notional / entry_price) * 1000000000000000000  # 0.1
    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notional * fee_rate
    is_long = True
    expect = 45000000000000000
    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual
