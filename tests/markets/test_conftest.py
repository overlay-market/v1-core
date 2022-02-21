from brownie import chain


def test_ovl_fixture(ovl):
    assert ovl.decimals() == 18
    assert ovl.name() == "Overlay"
    assert ovl.symbol() == "OVL"
    assert ovl.totalSupply() == 8000000000000000000000000


def test_factory_fixture(factory, ovl, fee_recipient):
    assert factory.ovl() == ovl
    assert factory.feeRecipient() == fee_recipient


def test_feed_fixture(feed, pool_daiweth_30bps, pool_uniweth_30bps, dai, weth,
                      uni):
    assert feed.marketPool() == pool_daiweth_30bps
    assert feed.ovlWethPool() == pool_uniweth_30bps
    assert feed.ovl() == uni
    assert feed.marketBaseAmount() == 1000000000000000000
    assert feed.marketBaseToken() == weth
    assert feed.marketQuoteToken() == dai
    assert feed.microWindow() == 600
    assert feed.macroWindow() == 3600


def test_mock_feed_fixture(mock_feed):
    assert mock_feed.microWindow() == 600
    assert mock_feed.macroWindow() == 3600
    assert mock_feed.price() == 1000000000000000000
    assert mock_feed.reserve() == 2000000000000000000000000


def test_mock_market_fixture(mock_market, mock_feed, ovl, factory, gov):
    # check addresses set properly
    assert mock_market.ovl() == ovl
    assert mock_market.feed() == mock_feed
    assert mock_market.factory() == factory

    # risk params
    assert mock_market.k() == 1220000000000
    assert mock_market.lmbda() == 1000000000000000000
    assert mock_market.delta() == 2500000000000000
    assert mock_market.capPayoff() == 5000000000000000000
    assert mock_market.capNotional() == 800000000000000000000000
    assert mock_market.capLeverage() == 5000000000000000000
    assert mock_market.circuitBreakerWindow() == 2592000
    assert mock_market.circuitBreakerMintTarget() == 66670000000000000000000
    assert mock_market.maintenanceMarginFraction() == 100000000000000000
    assert mock_market.maintenanceMarginBurnRate() == 100000000000000000
    assert mock_market.liquidationFeeRate() == 10000000000000000
    assert mock_market.tradingFeeRate() == 750000000000000
    assert mock_market.minCollateral() == 100000000000000
    assert mock_market.priceDriftUpperLimit() == 25000000000000

    # check mock market has minter and burner roles on ovl token
    assert ovl.hasRole(ovl.MINTER_ROLE(), mock_market) is True
    assert ovl.hasRole(ovl.BURNER_ROLE(), mock_market) is True

    # check oi related quantities are zero
    assert mock_market.oiLong() == 0
    assert mock_market.oiShort() == 0
    assert mock_market.oiLongShares() == 0
    assert mock_market.oiShortShares() == 0

    # check no positions exist
    assert mock_market.nextPositionId() == 0

    # check timestamp update last is same as block when mock_market deployed
    # NOTE: -3 in index since had two grantRole txs after in conftest.py
    assert mock_market.timestampUpdateLast() == chain[-3]["timestamp"]


def test_market_fixture(market, feed, ovl, factory, gov):
    # check addresses set properly
    assert market.ovl() == ovl
    assert market.feed() == feed
    assert market.factory() == factory

    # risk params
    assert market.k() == 1220000000000
    assert market.lmbda() == 1000000000000000000
    assert market.delta() == 2500000000000000
    assert market.capPayoff() == 5000000000000000000
    assert market.capNotional() == 800000000000000000000000
    assert market.capLeverage() == 5000000000000000000
    assert market.circuitBreakerWindow() == 2592000
    assert market.circuitBreakerMintTarget() == 66670000000000000000000
    assert market.maintenanceMarginFraction() == 100000000000000000
    assert market.maintenanceMarginBurnRate() == 100000000000000000
    assert market.liquidationFeeRate() == 10000000000000000
    assert market.tradingFeeRate() == 750000000000000
    assert market.minCollateral() == 100000000000000
    assert market.priceDriftUpperLimit() == 25000000000000

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
