from decimal import Decimal
from math import exp

from .utils import RiskParameter


def test_data_is_valid(market, feed, rando):
    tx = market.update({"from": rando})
    data = tx.return_value
    idx = RiskParameter.PRICE_DRIFT_UPPER_LIMIT.value

    _, _, _, _, price_macro_now, price_macro_ago, _, _ = data
    drift = (market.params(idx) / Decimal(1e18))

    macro_window = feed.macroWindow()
    dp = price_macro_now / price_macro_ago
    dp_lower_limit = exp(-drift * macro_window)
    dp_upper_limit = exp(drift * macro_window)

    expect = (dp >= dp_lower_limit and dp <= dp_upper_limit)
    actual = market.dataIsValid(data)
    assert expect == actual


def test_data_is_valid_when_dp_less_than_lower_limit(market, feed):
    tol = 1e-04
    idx = RiskParameter.PRICE_DRIFT_UPPER_LIMIT.value
    drift = (market.params(idx) / Decimal(1e18))
    _, micro_window, macro_window, _, _, _, _, _ = feed.latest()

    price_now = 2562676671798193257266

    # check data is not valid when price is less than lower limit
    pow = Decimal(drift) * Decimal(macro_window) * Decimal(1+tol)
    price_ago = int(price_now * exp(pow))
    data = (1643583611, 600, macro_window, 2569091057405103628119,
            price_now, price_ago,
            4677792160494647834844974, True)

    expect = False
    actual = market.dataIsValid(data)
    assert expect == actual

    # check data is valid when price is just above the lower limit
    pow = Decimal(drift) * Decimal(macro_window) * Decimal(1-tol)
    price_ago = int(price_now * exp(pow))
    data = (1643583611, micro_window, macro_window, 2569091057405103628119,
            price_now, price_ago,
            4677792160494647834844974, True)

    expect = True
    actual = market.dataIsValid(data)
    assert expect == actual


def test_data_is_valid_when_dp_greater_than_upper_limit(market, feed):
    tol = 1e-04
    idx = RiskParameter.PRICE_DRIFT_UPPER_LIMIT.value
    drift = (market.params(idx) / Decimal(1e18))
    _, micro_window, macro_window, _, _, _, _, _ = feed.latest()

    price_ago = 2562676671798193257266

    # check data is not valid when price is greater than upper limit
    pow = Decimal(drift) * Decimal(3000) * Decimal(1+tol)
    price_now = int(price_ago * exp(pow))
    data = (1643583611, micro_window, macro_window, 2569091057405103628119,
            price_now, price_ago,
            4677792160494647834844974, True)

    expect = False
    actual = market.dataIsValid(data)
    assert expect == actual

    # check data is valid when price is just below the upper limit
    pow = Decimal(drift) * Decimal(macro_window) * Decimal(1-tol)
    price_now = int(price_ago * exp(pow))
    data = (1643583611, micro_window, macro_window, 2569091057405103628119,
            price_now, price_ago,
            4677792160494647834844974, True)

    expect = True
    actual = market.dataIsValid(data)
    assert expect == actual


def test_data_is_valid_when_price_now_is_zero(market, feed):
    _, micro_window, macro_window, _, _, _, _, _ = feed.latest()
    data = (1643583611, micro_window, macro_window, 2569091057405103628119,
            0, 2565497026032266989873,
            4677792160494647834844974, True)
    expect = False
    actual = market.dataIsValid(data)
    assert expect == actual


def test_data_is_valid_when_price_ago_is_zero(market, feed):
    _, micro_window, macro_window, _, _, _, _, _ = feed.latest()
    data = (1643583611, micro_window, macro_window, 2569091057405103628119,
            2565497026032266989873, 0,
            4677792160494647834844974, True)
    expect = False
    actual = market.dataIsValid(data)
    assert expect == actual
