from brownie import reverts
from brownie.test import given, strategy
from decimal import Decimal
from math import exp
from pytest import approx

from .utils import RiskParameter


def test_bid_adds_static_spread(market, rando):
    # params idx for delta param
    idx = RiskParameter.DELTA.value

    # get the price data from call to update. update tests in test_update.py
    tx = market.update({"from": rando})
    data = tx.return_value
    _, _, _, price_micro, price_macro, _, _, _ = data

    delta = Decimal(market.params(idx) / 1e18)

    # use zero volume so no market impact
    volume = 0

    # bids get the lower of micro/macro prices (worse price), multiplied
    # by additional spread e^(-delta)
    expect_bid = int(min(price_micro, price_macro) * exp(-delta))
    actual_bid = int(market.bid(data, volume))
    assert actual_bid == approx(expect_bid)


@given(
    volume=strategy('decimal', min_value='0.0001', max_value='1.0000',
                    places=4))
def test_bid_adds_market_impact(market, volume, rando):
    # params idx for delta, lmbda params
    idx_delta = RiskParameter.DELTA.value
    idx_lmbda = RiskParameter.LMBDA.value

    # get the price data from call to update. update tests in test_update.py
    tx = market.update({"from": rando})
    data = tx.return_value
    _, _, _, price_micro, price_macro, _, _, _ = data

    delta = Decimal(market.params(idx_delta) / 1e18)
    lmbda = Decimal(market.params(idx_lmbda) / 1e18)

    # use volume anywhere from 0.1% to 100% of the cap
    input_volume = volume * Decimal(1e18)

    # bids get the lower of micro/macro prices (worse price), multiplied
    # by additional spread e^(-delta-lmbda*volume)
    expect_bid = int(min(price_micro, price_macro) * exp(-delta-lmbda*volume))
    actual_bid = int(market.bid(data, input_volume))
    assert actual_bid == approx(expect_bid)


def test_bid_reverts_when_slippage_greater_than_max(market, rando):
    # params idx for delta, lmbda params
    idx_delta = RiskParameter.DELTA.value
    idx_lmbda = RiskParameter.LMBDA.value

    # get the price data from call to update. update tests in test_update.py
    tx = market.update({"from": rando})
    data = tx.return_value
    _, _, _, price_micro, price_macro, _, _, _ = data

    delta = Decimal(market.params(idx_delta) / 1e18)
    lmbda = Decimal(market.params(idx_lmbda) / 1e18)

    # use volume greater than max slippage
    tol = 1e-4  # tolerance put at +/- 1bps
    max_pow = 20
    max_volume = (max_pow - delta) / lmbda

    # check reverts when volume produces slippage greater than max
    volume = Decimal(max_volume) * Decimal(1 + tol)
    input_volume = volume * Decimal(1e18)
    with reverts("OVLV1:slippage>max"):
        market.bid(data, input_volume)

    # check does not revert when volume produces slippage about equal to max
    volume = Decimal(max_volume) * Decimal(1 - tol)
    input_volume = volume * Decimal(1e18)
    _ = market.bid(data, input_volume)


def test_ask_adds_static_spread(market, rando):
    # params idx for delta param
    idx = RiskParameter.DELTA.value

    # get the price data from call to update. update tests in test_update.py
    tx = market.update({"from": rando})
    data = tx.return_value
    _, _, _, price_micro, price_macro, _, _, _ = data

    delta = Decimal(market.params(idx) / 1e18)

    # use zero volume so no market impact
    volume = 0

    # asks get the higher of micro/macro prices (worse price), multiplied
    # by additional spread e^(+delta)
    expect_ask = int(max(price_micro, price_macro) * exp(delta))
    actual_ask = int(market.ask(data, volume))
    assert actual_ask == approx(expect_ask)


@given(
    volume=strategy('decimal', min_value='0.0001', max_value='1.0000',
                    places=4))
def test_ask_adds_market_impact(market, volume, rando):
    # params idx for delta, lmbda params
    idx_delta = RiskParameter.DELTA.value
    idx_lmbda = RiskParameter.LMBDA.value

    # get the price data from call to update. update tests in test_update.py
    tx = market.update({"from": rando})
    data = tx.return_value
    _, _, _, price_micro, price_macro, _, _, _ = data

    delta = Decimal(market.params(idx_delta) / 1e18)
    lmbda = Decimal(market.params(idx_lmbda) / 1e18)

    # use volume anywhere from 0.1% to 100% of the cap
    input_volume = volume * Decimal(1e18)

    # asks get the higher of micro/macro prices (worse price), multiplied
    # by additional spread e^(delta+lmbda*volume)
    expect_ask = int(max(price_micro, price_macro) * exp(delta+lmbda*volume))
    actual_ask = int(market.ask(data, input_volume))
    assert actual_ask == approx(expect_ask)


def test_ask_reverts_when_impact_greater_than_max_slippage(market, rando):
    # params idx for delta, lmbda params
    idx_delta = RiskParameter.DELTA.value
    idx_lmbda = RiskParameter.LMBDA.value

    # get the price data from call to update. update tests in test_update.py
    tx = market.update({"from": rando})
    data = tx.return_value
    _, _, _, price_micro, price_macro, _, _, _ = data

    delta = Decimal(market.params(idx_delta) / 1e18)
    lmbda = Decimal(market.params(idx_lmbda) / 1e18)

    # use volume greater than max slippage
    tol = 1e-4  # tolerance put at +/- 1bps
    max_pow = 20
    max_volume = (max_pow - delta) / lmbda

    # check reverts when volume produces slippage greater than max
    volume = Decimal(max_volume) * Decimal(1 + tol)
    input_volume = volume * Decimal(1e18)
    with reverts("OVLV1:slippage>max"):
        market.ask(data, input_volume)

    # check does not revert when volume produces slippage about equal to max
    volume = Decimal(max_volume) * Decimal(1 - tol)
    input_volume = volume * Decimal(1e18)
    _ = market.ask(data, input_volume)
