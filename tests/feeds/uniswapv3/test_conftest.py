def test_token_fixtures(dai, weth, uni):
    assert dai.name() == "Dai Stablecoin"
    assert weth.name() == "Wrapped Ether"
    assert uni.name() == "Uniswap"


def test_pool_fixtures(dai, weth, uni, pool_daiweth_30bps, pool_uniweth_30bps):
    assert pool_daiweth_30bps.fee() == 3000
    assert pool_daiweth_30bps.token0() == dai
    assert pool_daiweth_30bps.token1() == weth

    assert pool_uniweth_30bps.fee() == 3000
    assert pool_uniweth_30bps.token0() == uni
    assert pool_uniweth_30bps.token1() == weth


def test_quanto_feed_fixture(dai, weth, uni, pool_daiweth_30bps,
                             pool_uniweth_30bps, quanto_feed):
    assert quanto_feed.microWindow() == 600
    assert quanto_feed.macroWindow() == 3600

    assert quanto_feed.marketPool() == pool_daiweth_30bps
    assert quanto_feed.ovlWethPool() == pool_uniweth_30bps
    assert quanto_feed.ovl() == uni

    assert quanto_feed.marketToken0() == dai
    assert quanto_feed.marketToken1() == weth
    assert quanto_feed.ovlWethToken0() == uni
    assert quanto_feed.ovlWethToken1() == weth

    assert quanto_feed.marketBaseToken() == weth
    assert quanto_feed.marketQuoteToken() == dai
    assert quanto_feed.marketBaseAmount() == 1 * 10 ** 18


def test_inverse_feed_fixture(dai, weth, uni, pool_daiweth_30bps,
                              pool_uniweth_30bps, inverse_feed):
    assert inverse_feed.microWindow() == 600
    assert inverse_feed.macroWindow() == 3600

    assert inverse_feed.marketPool() == pool_uniweth_30bps
    assert inverse_feed.ovlWethPool() == pool_uniweth_30bps
    assert inverse_feed.ovl() == uni

    assert inverse_feed.marketToken0() == uni
    assert inverse_feed.marketToken1() == weth
    assert inverse_feed.ovlWethToken0() == uni
    assert inverse_feed.ovlWethToken1() == weth

    assert inverse_feed.marketBaseToken() == weth
    assert inverse_feed.marketQuoteToken() == uni
    assert inverse_feed.marketBaseAmount() == 1 * 10 ** 18
