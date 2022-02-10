def test_set_price(feed):
    prior = feed.price()
    expect = prior * 5
    feed.setPrice(expect)

    actual = feed.price()
    assert actual == expect


def test_set_reserve(feed):
    prior = feed.reserve()
    expect = prior * 5
    feed.setReserve(expect)

    actual = feed.reserve()
    assert actual == expect
