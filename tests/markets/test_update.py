from brownie import chain


def test_update_fetches_from_feed(market, feed, rando):
    tx = market.update({"from": rando})
    actual = tx.return_value
    expect = feed.latest()
    assert actual == expect


# TODO:
def test_update_pays_funding(market, feed, rando):
    pass


def test_update_sets_last_timestamp(market, feed, rando):
    prior = market.timestampUpdateLast()

    # NOTE: oiAfterFunding() tests in test_funding.py
    # NOTE: feed.latest() tests in feeds/<feed>/test_latest.py
    tx = market.update()

    actual = market.timestampUpdateLast()
    expect = chain[tx.block_number]['timestamp']

    assert prior != actual
    assert expect == actual
