def test_feed_constructor(feed, gov):
    expect_micro_window = 600
    actual_micro_window = feed.microWindow()
    assert actual_micro_window == expect_micro_window

    expect_macro_window = 3600
    actual_macro_window = feed.macroWindow()
    assert actual_macro_window == expect_macro_window

    expect_feed_factory = gov
    actual_feed_factory = feed.feedFactory()
    assert expect_feed_factory == actual_feed_factory

    expect_price = 1000000000000000000
    actual_price = feed.price()
    assert actual_price == expect_price

    expect_reserve = 2000000000000000000000000
    actual_reserve = feed.reserve()
    assert actual_reserve == expect_reserve
