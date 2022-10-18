from pytest import approx


def test_get_quote_at_tick_for_daiweth_without_reserve(
        dai, weth, quanto_feed_without_reserve):
    # from Uniswap whitepaper: price = 1.0001^tick
    tick = -82944  # num_dai / num_weth ~ 4000
    base_amount = 1e18
    base_token = weth
    quote_token = dai

    # flip expect tick based off uniswap convention of base/quote if need to
    expect_sign = -1 if base_token.address > quote_token.address else 1
    expect_quote_amount = int(base_amount * 1.0001 ** (expect_sign * tick))

    actual_quote_amount = quanto_feed_without_reserve.getQuoteAtTick(
        tick, base_amount, base_token, quote_token
    )
    assert approx(expect_quote_amount) == actual_quote_amount


def test_get_quote_at_tick_for_daiweth(dai, weth, quanto_feed):
    # from Uniswap whitepaper: price = 1.0001^tick
    tick = -82944  # num_dai / num_weth ~ 4000
    base_amount = 1e18
    base_token = weth
    quote_token = dai

    # flip expect tick based off uniswap convention of base/quote if need to
    expect_sign = -1 if base_token.address > quote_token.address else 1
    expect_quote_amount = int(base_amount * 1.0001 ** (expect_sign * tick))

    actual_quote_amount = quanto_feed.getQuoteAtTick(
        tick, base_amount, base_token, quote_token
    )
    assert approx(expect_quote_amount) == actual_quote_amount


def test_get_quote_at_tick_for_uniweth(uni, weth, inverse_feed):
    # from Uniswap whitepaper: price = 1.0001^tick
    tick = -54262  # num_weth / num_uni ~ 0.0044
    base_amount = 1e18
    base_token = uni
    quote_token = weth

    # flip expect tick based off uniswap convention of base/quote if need to
    expect_sign = -1 if base_token.address > quote_token.address else 1
    expect_quote_amount = int(base_amount * 1.0001 ** (expect_sign * tick))

    actual_quote_amount = inverse_feed.getQuoteAtTick(
        tick, base_amount, base_token, quote_token
    )
    assert approx(expect_quote_amount) == actual_quote_amount


def test_get_reserve_in_weth_for_daiweth(weth, quanto_feed):
    # from Uniswap whitepaper:
    # x = liquidity / sqrtPrice; y = liquidity * sqrtPrice
    tick = -82944  # num_dai / num_weth ~ 4000
    liquidity = 12264526708744935729288014
    sqrt_price = 1.0001 ** (tick/2)

    expect_x = int(liquidity / sqrt_price)
    expect_y = int(liquidity * sqrt_price)

    expect_reserve = expect_x if quanto_feed.marketToken0 == weth else expect_y
    actual_reserve = quanto_feed.getReserveInX(tick, liquidity)
    assert approx(expect_reserve) == actual_reserve


def test_get_reserve_in_weth_for_uniweth(weth, inverse_feed):
    # from Uniswap whitepaper:
    # x = liquidity / sqrtPrice; y = liquidity * sqrtPrice
    tick = -54262  # num_weth / num_uni ~ 0.0044
    liquidity = 102094220270406915351232
    sqrt_price = 1.0001 ** (tick/2)

    expect_x = int(liquidity / sqrt_price)
    expect_y = int(liquidity * sqrt_price)

    expect_reserve = expect_x if inverse_feed.marketToken0 == weth \
        else expect_y
    actual_reserve = inverse_feed.getReserveInX(tick, liquidity)
    assert approx(expect_reserve) == actual_reserve


def test_get_reserve_in_ovl(uni, weth, quanto_feed):
    tick_market = -82944  # num_dai / num_weth ~ 4000
    tick_ovlweth = -54262  # num_weth / num_uni ~ 0.0044
    liquidity = 12264526708744935729288014  # market liquidity

    # get the expect market reserves in WETH
    sqrt_price_market = 1.0001 ** (tick_market/2)

    expect_x = int(liquidity / sqrt_price_market)
    expect_y = int(liquidity * sqrt_price_market)
    expect_reserve = expect_x if quanto_feed.marketToken0 == weth else expect_y

    # get the price of UNI/WETH (ovl=UNI in tests)
    base_amount_ovlweth = 1e18
    base_token_ovlweth = uni
    quote_token_ovlweth = weth

    # flip expect tick based off uniswap convention of base/quote if need to
    sign = -1 if base_token_ovlweth.address > quote_token_ovlweth.address \
        else 1

    # num of WETH / num of UNI
    price_ovlweth = int(base_amount_ovlweth * 1.0001 ** (sign * tick_ovlweth))

    expect_reserve_in_ovl = int(expect_reserve
                                * base_amount_ovlweth / price_ovlweth)
    actual_reserve_in_ovl = quanto_feed.getReserveInOvl(tick_market, liquidity,
                                                        tick_ovlweth)
    assert approx(expect_reserve_in_ovl) == actual_reserve_in_ovl


# TODO: tests if have WETH as token0 vs token1
# for quanto and inverse
