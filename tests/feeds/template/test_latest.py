import brownie


def test_latest_updates_data_on_first_call(feed):
    timestamp = brownie.chain.time()
    micro_window = feed.microWindow()
    macro_window = feed.macroWindow()
    price = feed.price()
    reserve = feed.reserve()

    # check new data returned
    expect = (timestamp, micro_window, macro_window, price, price,
              reserve, reserve)
    actual = feed.latest()
    assert actual == expect


def test_latest_updates_data_on_many_calls(feed):
    for i in range(3):
        # fetch from feed 3 times in a row w 60s in between
        brownie.chain.mine(timedelta=60)

        timestamp = brownie.chain.time()
        micro_window = feed.microWindow()
        macro_window = feed.macroWindow()
        price = feed.price()
        reserve = feed.reserve()

        expect = (timestamp, micro_window, macro_window, price, price,
                  reserve, reserve)
        actual = feed.latest()
        assert actual == expect
