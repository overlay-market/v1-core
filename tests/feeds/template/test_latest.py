import brownie

def test_latest_updates_data_on_first_call(feed):
    timestamp = brownie.chain.time()
    micro_window = feed.microWindow()
    macro_window = feed.macroWindow()
    price = feed.price()
    reserves = feed.reserves()

    expect = (timestamp, micro_window, macro_window, price, price,
              reserves, reserves)
    tx = feed.latest()
    actual = tx.return_value
    assert actual == expect

    expect_oracle_data_last = expect
    actual_oracle_data_last = feed.oracleDataLast()
    assert actual_oracle_data_last == expect_oracle_data_last
