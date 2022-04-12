from brownie import chain
from brownie.test import given, strategy
from decimal import Decimal

from .utils import RiskParameter


# SN TODO: copy this w balancerv2 feed to get latest gas estimates
#
def test_update_fetches_from_feed(market, feed, rando):
    # call update
    tx = market.update({"from": rando})

    # NOTE: feed.latest() tests in feeds/<feed>/test_latest.py
    actual = tx.return_value
    expect = feed.latest()
    assert actual == expect


@given(
    notional_long=strategy('decimal', min_value='0.001', max_value='800000',
                           places=3),
    notional_short=strategy('decimal', min_value='0.001', max_value='800000',
                            places=3))
def test_update_pays_funding(market, feed, ovl, alice, bob, rando,
                             notional_long, notional_short):
    idx_trade = RiskParameter.TRADING_FEE_RATE.value

    notional_long = notional_long * Decimal(1e18)
    notional_short = notional_short * Decimal(1e18)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.params(idx_trade) / 1e18)
    approve_collateral_long = notional_long * (1 + trading_fee_rate)
    approve_collateral_short = notional_short * (1 + trading_fee_rate)

    # approve collateral amounts
    ovl.approve(market, approve_collateral_long, {"from": alice})
    ovl.approve(market, approve_collateral_short, {"from": bob})

    # build long and short positions for oi
    # NOTE: build() tests in test_build.py
    _ = market.build(notional_long, 1e18, True, 2**256-1, {"from": alice})
    _ = market.build(notional_short, 1e18, False, 0, {"from": bob})

    # get values prior to mine chain
    expect_oi_long = market.oiLong()
    expect_oi_short = market.oiShort()
    timestamp_last = market.timestampUpdateLast()

    # mine chain into the future
    chain.mine(timedelta=600)

    # call update
    tx = market.update({"from": rando})
    timestamp_now = chain[tx.block_number]['timestamp']
    time_elapsed = timestamp_now - timestamp_last

    # NOTE: oiAfterFunding() tests in test_funding.py
    if (expect_oi_long > expect_oi_short):
        expect_oi_long, expect_oi_short = market.oiAfterFunding(
            expect_oi_long, expect_oi_short, time_elapsed)
    else:
        expect_oi_short, expect_oi_long = market.oiAfterFunding(
            expect_oi_short, expect_oi_long, time_elapsed)

    actual_oi_long = market.oiLong()
    actual_oi_short = market.oiShort()

    # check oi long and short stored after funding calc
    assert expect_oi_long == actual_oi_long
    assert expect_oi_short == actual_oi_short


def test_update_sets_last_timestamp(market, rando):
    # prior is timestamp is timestamp when deployed in conftest.py
    prior = market.timestampUpdateLast()

    # mine the chain 60s into the future
    chain.mine(timedelta=60)

    # call update
    tx = market.update({"from": rando})

    # check timestamp updated to last block timestamp
    actual = market.timestampUpdateLast()
    expect = chain[tx.block_number]['timestamp']
    assert expect == actual
    assert prior != actual
