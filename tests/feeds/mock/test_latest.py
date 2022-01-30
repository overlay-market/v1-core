from brownie import chain


def test_latest_updates_data_on_first_call(feed):
    micro_window = feed.microWindow()
    macro_window = feed.macroWindow()
    price = feed.price()
    reserve = feed.reserve()
    has_reserve = True
    timestamp = chain[-1]['timestamp']

    # check new data returned
    expect = (timestamp, micro_window, macro_window, price, price,
              price, reserve, has_reserve)
    actual = feed.latest()
    assert actual == expect


def test_latest_updates_data_on_many_calls(feed):
    for i in range(3):
        # fetch from feed 3 times in a row w 60s in between
        chain.mine(timedelta=60)

        micro_window = feed.microWindow()
        macro_window = feed.macroWindow()
        price = feed.price()
        reserve = feed.reserve()
        has_reserve = True
        timestamp = chain[-1]['timestamp']

        expect = (timestamp, micro_window, macro_window, price, price,
                  price, reserve, has_reserve)
        actual = feed.latest()
        assert actual == expect
