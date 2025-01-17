from pytest import approx
from brownie import reverts
from brownie.test import given, strategy
from decimal import Decimal
from math import log, pow


# NOTE: only care to 4 decimals but use 6 for testing
@given(price=strategy('decimal', min_value='0.000001', places=6))
def test_price_to_tick(tick_mock, price):
    base = Decimal(1.0001)
    input_price = price * Decimal(1e18)
    output_tick = tick_mock.priceToTick(input_price)

    expect = int(log(price) / log(base))
    actual = output_tick
    assert expect == actual


@given(tick=strategy('int24', min_value='-410000', max_value='1200000'))
def test_tick_to_price(tick_mock, tick):
    base = Decimal(1.0001)
    input_tick = tick
    output_price = tick_mock.tickToPrice(input_tick)

    expect = int(Decimal(pow(base, tick)) * Decimal(1e18))
    actual = int(output_price)

    assert expect == approx(actual, rel=1e-4)


# NOTE: make sure unitary
@given(price=strategy('decimal', min_value='2e-18'))
def test_price_to_tick_to_price(tick_mock, price):
    input_price = price * Decimal(1e18)
    output_tick = tick_mock.priceToTick(input_price)
    output_price = tick_mock.tickToPrice(output_tick)

    expect = int(input_price)
    actual = int(output_price)

    # precision given base of 1.0001 only to 4 decimals (1 bps)
    assert expect == approx(actual, rel=1e-4)


def test_price_to_tick_reverts_when_lt_min(tick_mock):
    # check passes for input price of 2 FixedPoint (= 1e-18 float)
    base = Decimal(1.0001)
    input_price = 2
    price = Decimal(input_price) / Decimal(1e18)

    actual = tick_mock.priceToTick(input_price)
    expect = int(log(price) / log(base))
    assert expect == actual

    # check reverts when input price 1 less (equal to zero)
    input_price = 1
    with reverts("OVLV1: tick out of bounds"):
        tick_mock.priceToTick(input_price)


def test_price_to_tick_reverts_when_gt_max(tick_mock):
    # check passes for input price of 1.0001 ** (120 * 1e4)
    input_price = int(Decimal(1.0001) ** Decimal(1200000) * Decimal(1e18))

    actual = tick_mock.priceToTick(input_price)
    expect = 1199999  # rounding issues at 1200000
    assert expect == actual

    # check reverts when input price is 1 bps less
    input_price = int(input_price * (1.0001))
    with reverts("OVLV1: tick out of bounds"):
        tick_mock.priceToTick(input_price)


def test_tick_to_price_reverts_when_lt_min(tick_mock):
    # reverts when smaller than min tick
    input_tick = -(410000 + 1)
    with reverts("OVLV1: tick out of bounds"):
        tick_mock.tickToPrice(input_tick)

    # doesn't revert when equal to min tick
    input_tick = -410000
    actual = tick_mock.tickToPrice(input_tick)
    expect = 1
    assert expect == actual


def test_tick_to_price_reverts_when_gt_max(tick_mock):
    base = Decimal(1.0001)
    # reverts when larger than max tick
    input_tick = (1200000 + 1)
    with reverts("OVLV1: tick out of bounds"):
        tick_mock.tickToPrice(input_tick)

    # doesn't revert when equal to max tick
    input_tick = 1200000
    actual = int(tick_mock.tickToPrice(input_tick))
    expect = int(Decimal(pow(base, input_tick)) * Decimal(1e18))
    assert expect == approx(actual, rel=1e-4)
