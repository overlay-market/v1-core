from decimal import Decimal
from pytest import approx


def test_cap_oi_front_run_bound(market, feed):
    lmbda = Decimal(market.lmbda()) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    # TODO: generalize for any feed
    _, _, _, _, _, reserve_micro, _, _ = data

    # check front run bound is lmbda * reserveOverMicro / 2 when has reserve
    expect = int(lmbda * Decimal(reserve_micro) / Decimal(2))
    actual = market.capOiFrontRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_oi_front_run_bound_when_no_reserve(market, feed):
    cap_oi = market.capOi()
    data = (1642797758, 600, 3600, 2729583770051358617413,
            2739701430255362520176, 1918499886987334209868033,
            1909229154186640322863637, False)  # has_reserve = False

    # check front run bound is cap_oi when no reserve
    expect = cap_oi
    actual = market.capOiFrontRunBound(data)
    assert actual == expect


def test_cap_oi_back_run_bound(market, feed):
    delta = Decimal(market.delta()) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    # TODO: generalize for any feed
    average_block_time = 14
    _, _, macro_window, _, _, reserve_micro, _, _ = data

    # check front run bound is lmbda * reserveOverMicro / 2 when has reserve
    window = Decimal(macro_window) / Decimal(average_block_time)
    expect = int(Decimal(2) * delta * Decimal(reserve_micro) * window)
    actual = market.capOiBackRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_oi_back_run_bound_when_no_reserve(market):
    cap_oi = market.capOi()
    data = (1642797758, 600, 3600, 2729583770051358617413,
            2739701430255362520176, 1918499886987334209868033,
            1909229154186640322863637, False)  # has_reserve = False

    # check back run bound is cap_oi when no reserve
    expect = cap_oi
    actual = market.capOiBackRunBound(data)
    assert actual == expect
