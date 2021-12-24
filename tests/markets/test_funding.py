import pytest


# use isolation to reset state for each test in the file
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_pay_funding_when_longs_and_shorts_are_zero(market, feed, rando):
    _ = market.payFunding()
    assert market.oiLong() == 0
    assert market.oiShort() == 0
    assert market.oiLongShares() == 0
    assert market.oiShortShares() == 0


def test_pay_funding_when_longs_outweigh_shorts(market, feed, rando):
    pass


def test_pay_funding_when_shorts_are_zero(market, feed, rando):
    pass


def test_pay_funding_when_longs_are_zero(market, feed, rando):
    pass
