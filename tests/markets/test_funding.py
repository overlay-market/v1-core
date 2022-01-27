def test_oi_after_funding_when_longs_and_shorts_are_zero(market):
    oi_long = 0
    oi_short = 0
    timestamp_last = 1643247197
    timestamp_now = 1643247797

    actual_oi_overweight, actual_oi_underweight = market.oiAfterFunding(
        oi_long, oi_short, timestamp_last, timestamp_now)

    assert actual_oi_overweight == 0
    assert actual_oi_underweight == 0


# TODO:
def test_oi_after_funding_when_longs_outweigh_shorts(market, feed, rando):
    pass


# TODO:
def test_oi_after_funding_when_shorts_are_zero(market, feed, rando):
    pass


# TODO:
def test_oi_after_funding_when_longs_are_zero(market, feed, rando):
    pass
