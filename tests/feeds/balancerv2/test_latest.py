from brownie import chain


def test_latest_updates_data_on_first_call_for_quanto_feed(pool_daiweth,
                                                           pool_balweth,
                                                           feed):
    macro_window = feed.macroWindow()
    micro_window = feed.microWindow()
    timestamp = chain[-1]['timestamp']
    pool_market = feed.marketPool()

    variable = 0  # PAIR_PRICE
    ago = 0
    query = feed.getOracleAverageQuery(variable, micro_window, ago)
    price_over_micro_window = feed.getTimeWeightedAverage(pool_market,
                                                          [query])[0]

    prices = feed.getPairPrices()
    reserve = feed.getReserve(price_over_micro_window)
    has_reserve = True

    expect = (timestamp, micro_window, macro_window, prices[0], prices[1],
              prices[2], reserve, has_reserve)

    actual = feed.latest()

    assert expect == actual
