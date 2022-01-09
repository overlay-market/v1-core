from brownie import chain


def test_update_fetches_from_feed(market, feed, rando):
    tx = market.update({"from": rando})
    actual = tx.return_value
    expect = feed.latest()
    assert actual == expect


def test_update_pays_funding(market, feed, rando):
    prior = market.fundingPaidLast()

    # NOTE: payFunding() tests in test_funding.py
    tx = market.update()

    actual = market.fundingPaidLast()
    expect = chain[tx.block_number]['timestamp']

    assert prior != actual
    assert expect == actual
