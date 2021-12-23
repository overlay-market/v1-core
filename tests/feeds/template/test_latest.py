import brownie
from collections import OrderedDict


def test_latest_updates_data_on_first_call(feed):
    timestamp = brownie.chain.time()
    micro_window = feed.microWindow()
    macro_window = feed.macroWindow()
    price = feed.price()
    reserve = feed.reserve()

    # check new data returned
    expect = (timestamp, micro_window, macro_window, price, price,
              reserve, reserve)

    tx = feed.latest()
    actual = tx.return_value

    assert actual == expect

    # check oracleDataLast state changed
    expect_oracle_data_last = expect
    actual_oracle_data_last = feed.oracleDataLast()
    assert actual_oracle_data_last == expect_oracle_data_last

    # check event emitted
    assert 'Fetch' in tx.events
    expect_event = OrderedDict({
        'priceOverMicroWindow': price,
        'priceOverMacroWindow': price,
        'reserveOverMicroWindow': reserve,
        'reserveOverMacroWindow': reserve,
    })
    actual_event = tx.events['Fetch']
    assert expect_event == actual_event


def test_latest_updates_data_on_subsequent_calls(feed):
    actual_oracle_data_last = feed.oracleDataLast()

    for i in range(3):
        brownie.chain.mine(timedelta=1)

        timestamp = brownie.chain.time()
        micro_window = feed.microWindow()
        macro_window = feed.macroWindow()
        price = feed.price()
        reserve = feed.reserve()

        expect = (timestamp, micro_window, macro_window, price, price,
                  reserve, reserve)

        tx = feed.latest()
        actual = tx.return_value

        assert actual == expect

        # state was updated since time passed
        assert actual != actual_oracle_data_last

        expect_oracle_data_last = expect
        actual_oracle_data_last = feed.oracleDataLast()

        assert actual_oracle_data_last == expect_oracle_data_last
