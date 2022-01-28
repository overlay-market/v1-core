from brownie import chain


def test_ovl_fixture(ovl):
    assert ovl.decimals() == 18
    assert ovl.name() == "Overlay"
    assert ovl.symbol() == "OVL"
    assert ovl.totalSupply() == 8000000000000000000000000


def test_feed_fixture(feed, pool_daiweth_30bps, pool_uniweth_30bps, dai, weth,
                      uni):
    assert feed.marketPool() == pool_daiweth_30bps
    assert feed.ovlWethPool() == pool_uniweth_30bps
    assert feed.ovl() == uni
    assert feed.marketBaseAmount() == 1000000000000000000
    assert feed.marketBaseToken() == weth
    assert feed.marketQuoteToken() == dai


def test_market_fixture(market, feed, ovl, gov):
    assert market.ovl() == ovl
    assert market.feed() == feed
    assert market.factory() == gov
    assert market.tradingFeeRecipient() == gov

    # risk params
    assert market.k() == 1220000000000
    assert market.lmbda() == 1000000000000000000
    assert market.delta() == 2500000000000000
    assert market.capPayoff() == 5000000000000000000
    assert market.capOi() == 800000000000000000000000
    assert market.capLeverage() == 5000000000000000000
    assert market.circuitBreakerWindow() == 2592000
    assert market.circuitBreakerMintTarget() == 66670000000000000000000
    assert market.maintenanceMargin() == 100000000000000000
    assert market.maintenanceMarginBurnRate() == 100000000000000000
    assert market.tradingFeeRate() == 750000000000000
    assert market.minCollateral() == 100000000000000

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

    # check timestamp update last is same as block when market was deployed
    # NOTE: -3 in index since had two grantRole txs after in conftest.py
    assert market.timestampUpdateLast() == chain[-3]["timestamp"]
