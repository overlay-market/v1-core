def test_feed_constructor(feed):
    actual_micro_window = 600
    expect_micro_window = feed.microWindow()
    assert actual_micro_window == expect_micro_window

    actual_macro_window = 3600
    expect_macro_window = feed.macroWindow()
    assert actual_macro_window == expect_macro_window

    actual_price = 1000000000000000000
    expect_price = feed.price()
    assert actual_price == expect_price

    actual_reserves = 2000000000000000000
    expect_reserves = feed.reserves()
    assert actual_reserves == expect_reserves


def test_feed_oracle_data_last(feed):
    expect = (0, 0, 0, 0, 0, 0, 0)
    actual = feed.oracleDataLast()
    assert actual == expect
