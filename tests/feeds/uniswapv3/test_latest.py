import brownie
from collections import OrderedDict


def test_latest_updates_data_for_quanto_feed(pool_daiweth_30bps,
                                             pool_uniweth_30bps,
                                             quanto_feed):
    timestamp = brownie.chain.time()
    micro_window = quanto_feed.microWindow()
    macro_window = quanto_feed.macroWindow()
    market_base_amount = quanto_feed.marketBaseAmount()
    market_base_token = quanto_feed.marketBaseToken()
    market_quote_token = quanto_feed.marketQuoteToken()

    tx = quanto_feed.latest()
    actual = tx.return_value

    # calculate the avg tick and liquidity values from pool.observe cumulatives
    seconds_agos = [macro_window, micro_window, 0]
    market_avg_ticks, market_avg_liqs = quanto_feed.consult(
        pool_daiweth_30bps, seconds_agos)
    ovlweth_avg_ticks, ovlweth_avg_liqs = quanto_feed.consult(
        pool_uniweth_30bps, seconds_agos)

    prices = []
    reserves = []
    for i in range(2):
        # NOTE: getQuoteAtTick(), getReserveInOvl() tested in test_views.py
        price = quanto_feed.getQuoteAtTick(
            market_avg_ticks[i], market_base_amount,
            market_base_token, market_quote_token)
        reserve = quanto_feed.getReserveInOvl(
            market_avg_ticks[i], market_avg_liqs[i], ovlweth_avg_ticks[i])

        prices.append(price)
        reserves.append(reserve)

    expect = (timestamp, micro_window, macro_window, prices[1], prices[0],
              reserves[1], reserves[0])

    assert expect == actual

    # check event emitted
    assert 'Fetch' in tx.events
    expect_event = OrderedDict({
        'priceOverMicroWindow': prices[1],
        'priceOverMacroWindow': prices[0],
        'reserveOverMicroWindow': reserves[1],
        'reserveOverMacroWindow': reserves[0],
    })
    actual_event = tx.events['Fetch']

    assert expect_event == actual_event


def test_latest_updates_data_for_inverse_feed(pool_uniweth_30bps,
                                              inverse_feed):
    timestamp = brownie.chain.time()
    micro_window = inverse_feed.microWindow()
    macro_window = inverse_feed.macroWindow()
    market_base_amount = inverse_feed.marketBaseAmount()
    market_base_token = inverse_feed.marketBaseToken()
    market_quote_token = inverse_feed.marketQuoteToken()

    tx = inverse_feed.latest()
    actual = tx.return_value

    # calculate the avg tick and liquidity values from pool.observe cumulatives
    seconds_agos = [macro_window, micro_window, 0]
    market_avg_ticks, market_avg_liqs = inverse_feed.consult(
        pool_uniweth_30bps, seconds_agos)
    ovlweth_avg_ticks, ovlweth_avg_liqs = inverse_feed.consult(
        pool_uniweth_30bps, seconds_agos)

    prices = []
    reserves = []
    for i in range(2):
        # NOTE: getQuoteAtTick(), getReserveInOvl() tested in test_views.py
        price = inverse_feed.getQuoteAtTick(
            market_avg_ticks[i], market_base_amount,
            market_base_token, market_quote_token)
        reserve = inverse_feed.getReserveInOvl(
            market_avg_ticks[i], market_avg_liqs[i], ovlweth_avg_ticks[i])

        prices.append(price)
        reserves.append(reserve)

    expect = (timestamp, micro_window, macro_window, prices[1], prices[0],
              reserves[1], reserves[0])

    assert expect == actual

    # check event emitted
    assert 'Fetch' in tx.events
    expect_event = OrderedDict({
        'priceOverMicroWindow': prices[1],
        'priceOverMacroWindow': prices[0],
        'reserveOverMicroWindow': reserves[1],
        'reserveOverMacroWindow': reserves[0],
    })
    actual_event = tx.events['Fetch']

    assert expect_event == actual_event
