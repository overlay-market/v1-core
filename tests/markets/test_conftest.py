def test_ovl_fixture(ovl):
    assert ovl.decimals() == 18
    assert ovl.name() == "Overlay"
    assert ovl.symbol() == "OVL"
    assert ovl.totalSupply() == 8000000000000000000000000


def test_feed_fixture(feed, pool_daiweth_30bps, pool_uniweth_30bps, dai, weth,
                      uni):
    feed.marketPool() == pool_daiweth_30bps
    feed.ovlWethPool() == pool_uniweth_30bps
    feed.ovl() == uni
    feed.marketBaseAmount() == 1000000000000000000
    feed.marketBaseToken() == weth
    feed.marketQuoteToken() == dai


def test_market_fixture(market, feed, ovl, gov):
    market.ovl() == ovl
    market.feed() == feed
    market.factory() == gov
    market.tradingFeeRecipient() == gov

    # risk params
    market.k() == 8587500000000
    market.lmbda() == 1000000000000000000
    market.delta() == 2500000000000000
    market.capPayoff() == 5000000000000000000
    market.capOi() == 800000000000000000000000
    market.capLeverage() == 5000000000000000000
    market.maintenanceMargin() == 100000000000000000
    market.maintenanceMarginBurnRate() == 100000000000000000
    market.tradingFeeRate() == 750000000000000
    market.minCollateral() == 100000000000000

    # check market has minter and burner roles on ovl token
    assert ovl.hasRole(ovl.MINTER_ROLE(), market) is True
    assert ovl.hasRole(ovl.BURNER_ROLE(), market) is True

    # check oi related quantities are zero
    assert market.oiLong() == 0
    assert market.oiShort() == 0
    assert market.oiLongShares() == 0
    assert market.oiShortShares() == 0

    # check no positions exist
    assert market.nextPositionId() == 0
