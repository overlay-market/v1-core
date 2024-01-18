from brownie import chain
from pytest import approx


def test_latest_data(mock_aggregator,
                     chainlink_feed, gov):
    # set initial reading of 10e8
    mock_aggregator.setData(1, 10e8, {"from": gov})

    chain.mine(timedelta=3600)

    price_data = chainlink_feed.latest()

    (_time, _micro_window, _macro_window, price_over_micro_window,
     price_over_macro_window, price_one_macro_window_ago,
     _reserve_over_micro_window, _has_reserve) = price_data

    assert 10e18 == approx(price_over_micro_window)
    assert 10e18 == approx(price_over_macro_window)
    assert 0 == approx(price_one_macro_window_ago, rel=1e14)

    mock_aggregator.setData(2, 12e8, {"from": gov})

    chain.mine(timedelta=3000)
    # micro price = 12e18, macro price = 12*3000+10*600/3600 = 11.667
    # price macro window ago = 10e18

    price_data = chainlink_feed.latest()

    micro_price_expect = 12e18
    macro_price_expect = (10*600 + 12*3000)*1e18/3600

    macro_ago_price_expect = 10*3000*1e18/3600

    (_time, _micro_window, _macro_window, price_over_micro_window,
     price_over_macro_window, price_one_macro_window_ago,
     _reserve_over_micro_window, _has_reserve) = price_data

    assert micro_price_expect == approx(price_over_micro_window)
    assert macro_price_expect == approx(price_over_macro_window, rel=1e14)
    assert macro_ago_price_expect == approx(
        price_one_macro_window_ago, rel=1e14)
