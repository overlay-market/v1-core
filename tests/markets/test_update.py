from brownie import chain
from brownie.test import given, strategy
from decimal import Decimal


def test_update_fetches_from_feed(market, feed, rando):
    # call update
    tx = market.update({"from": rando})

    # NOTE: feed.latest() tests in feeds/<feed>/test_latest.py
    actual = tx.return_value
    expect = feed.latest()
    assert actual == expect


@given(
    oi_long=strategy('decimal', min_value='0.001', max_value='800000',
                     places=3),
    oi_short=strategy('decimal', min_value='0.001', max_value='800000',
                      places=3))
def test_update_pays_funding(market, feed, ovl, alice, bob, oi_long, oi_short):
    oi_long = oi_long * Decimal(1e18)
    oi_short = oi_short * Decimal(1e18)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    approve_collateral_long = oi_long * (1 + trading_fee_rate)
    approve_collateral_short = oi_short * (1 + trading_fee_rate)

    # approve collateral amounts
    ovl.approve(market, approve_collateral_long, {"from": alice})
    ovl.approve(market, approve_collateral_short, {"from": bob})

    # build long and short positions for oi
    # NOTE: build() tests in test_build.py
    _ = market.build(oi_long, 1e18, True, {"from": alice})
    _ = market.build(oi_short, 1e18, False, {"from": bob})

    # get values prior to mine chain
    expect_oi_long = market.oiLong()
    expect_oi_short = market.oiShort()
    timestamp_last = market.timestampUpdateLast()

    # mine chain into the future
    chain.mine(timedelta=600)

    # call update
    tx = market.update()
    timestamp_now = chain[tx.block_number]['timestamp']

    # NOTE: oiAfterFunding() tests in test_funding.py
    if (expect_oi_long > expect_oi_short):
        expect_oi_long, expect_oi_short = market.oiAfterFunding(
            expect_oi_long, expect_oi_short, timestamp_last, timestamp_now)
    else:
        expect_oi_short, expect_oi_long = market.oiAfterFunding(
            expect_oi_short, expect_oi_long, timestamp_last, timestamp_now)

    actual_oi_long = market.oiLong()
    actual_oi_short = market.oiShort()

    # check oi long and short stored after funding calc
    assert expect_oi_long == actual_oi_long
    assert expect_oi_short == actual_oi_short


def test_update_sets_last_timestamp(market, feed, rando):
    # prior is timestamp is timestamp when deployed in conftest.py
    prior = market.timestampUpdateLast()

    # mine the chain 60s into the future
    chain.mine(timedelta=60)

    # call update
    tx = market.update()

    # check timestamp updated to last block timestamp
    actual = market.timestampUpdateLast()
    expect = chain[tx.block_number]['timestamp']
    assert expect == actual
    assert prior != actual
