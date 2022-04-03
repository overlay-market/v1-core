def test_token_fixtures(dai, weth, uni):
    assert dai.name() == "Dai Stablecoin"
    assert weth.name() == "Wrapped Ether"
    assert uni.name() == "Uniswap"


def test_pool_fixtures(dai, weth, uni, uni_factory, pool_daiweth_30bps,
                       pool_uniweth_30bps):
    assert pool_daiweth_30bps.fee() == 3000
    assert pool_daiweth_30bps.token0() == dai
    assert pool_daiweth_30bps.token1() == weth
    assert pool_daiweth_30bps == uni_factory.getPool(dai, weth, 3000)

    assert pool_uniweth_30bps.fee() == 3000
    assert pool_uniweth_30bps.token0() == uni
    assert pool_uniweth_30bps.token1() == weth
    assert pool_uniweth_30bps == uni_factory.getPool(uni, weth, 3000)


def test_quanto_feed_fixture(dai, weth, uni, pool_daiweth_30bps,
                             pool_uniweth_30bps, quanto_feed, gov):
    assert quanto_feed.microWindow() == 600
    assert quanto_feed.macroWindow() == 3600
    assert quanto_feed.feedFactory() == gov

    assert quanto_feed.marketPool() == pool_daiweth_30bps
    assert quanto_feed.ovlXPool() == pool_uniweth_30bps

    assert quanto_feed.marketToken0() == dai
    assert quanto_feed.marketToken1() == weth

    assert quanto_feed.marketBaseToken() == weth
    assert quanto_feed.marketQuoteToken() == dai
    assert quanto_feed.marketBaseAmount() == 1 * 10 ** 18

    assert quanto_feed.ovl() == uni
    assert quanto_feed.x() == weth


def test_inverse_feed_fixture(dai, weth, uni, pool_daiweth_30bps,
                              pool_uniweth_30bps, inverse_feed, gov):
    assert inverse_feed.microWindow() == 600
    assert inverse_feed.macroWindow() == 3600
    assert inverse_feed.feedFactory() == gov

    assert inverse_feed.marketPool() == pool_uniweth_30bps
    assert inverse_feed.ovlXPool() == pool_uniweth_30bps

    assert inverse_feed.marketToken0() == uni
    assert inverse_feed.marketToken1() == weth

    assert inverse_feed.marketBaseToken() == weth
    assert inverse_feed.marketQuoteToken() == uni
    assert inverse_feed.marketBaseAmount() == 1 * 10 ** 18

    assert inverse_feed.ovl() == uni
    assert inverse_feed.x() == weth
