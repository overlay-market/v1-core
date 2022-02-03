from brownie.test import given, strategy
from decimal import Decimal


def test_trading_fee(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    trading_fee_rate = 750000000000000

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notional * fee_rate
    is_long = True
    expect = 11250000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is notional * fee_rate
    is_long = False
    expect = 3750000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is oi * fee_rate when 0 price change
    is_long = True
    current_price = entry_price
    expect = 7500000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is oi * fee_rate when 0 price change
    is_long = False
    current_price = entry_price
    expect = 7500000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual


def test_trading_fee_when_fraction_less_than_one(position):
    entry_price = 100000000000000000000  # 100
    current_price = 150000000000000000000  # 150
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    trading_fee_rate = 750000000000000

    fraction = 250000000000000000  # 0.25
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notional * fee_rate
    is_long = True
    expect = 2812500000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual

    # check trading fee is notional * fee_rate
    is_long = False
    expect = 937500000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual


@given(payoff=strategy('decimal', min_value='5', max_value='100', places=3))
def test_trading_fee_when_payoff_greater_than_cap(position, payoff):
    entry_price = 100000000000000000000  # 100
    current_price = int(Decimal(entry_price) * (Decimal(1) + payoff))
    oi = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False
    trading_fee_rate = 750000000000000

    fraction = 1000000000000000000  # 1
    cap_payoff = 5000000000000000000  # 5

    # check trading fee is notional * fee_rate
    is_long = True
    expect = 45000000000000000
    pos = (oi, debt, is_long, liquidated, entry_price)
    actual = position.tradingFee(pos, fraction, oi, oi, current_price,
                                 cap_payoff, trading_fee_rate)
    assert expect == actual
