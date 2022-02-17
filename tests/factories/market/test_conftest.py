def test_factory_fixture(factory, fee_recipient, feed_factory, feed_three, ovl,
                         gov, market, deployer):
    # check ovl immutable set
    assert factory.ovl() == ovl

    # check fee recipient set
    assert factory.feeRecipient() == fee_recipient

    # check deployer contract deployed on factory deploy
    assert factory.deployer() != "0x0000000000000000000000000000000000000000"
    assert deployer.factory() == factory

    # check factory has been given admin role on ovl token
    assert ovl.hasRole(ovl.ADMIN_ROLE(), factory) is True

    # check gov has been given governance role on ovl token
    assert ovl.hasRole(ovl.GOVERNOR_ROLE(), gov) is True

    # check feed factory has been added to registry
    assert factory.isFeedFactory(feed_factory) is True

    # check market deployed for feed three has been added to registry
    assert factory.getMarket(feed_three) == market
    assert factory.isMarket(market) is True


def test_feed_factory_fixture(feed_factory, feed_one, feed_two, feed_three):
    # check params set properly
    assert feed_factory.microWindow() == 600
    assert feed_factory.macroWindow() == 3600

    # check feeds with (price, reserve) combos have been deployed
    assert feed_factory.isFeed(feed_one) is True
    assert feed_factory.isFeed(feed_two) is True
    assert feed_factory.isFeed(feed_three) is True


def test_market_fixture(market, factory, feed_three, ovl, gov):
    # check params set properly
    # NOTE: market fixture uses feed three
    assert market.ovl() == ovl
    assert market.factory() == factory
    assert market.feed() == feed_three

    assert market.k() == 1220000000000
    assert market.lmbda() == 1000000000000000000
    assert market.delta() == 2500000000000000
    assert market.capPayoff() == 5000000000000000000
    assert market.capOi() == 800000000000000000000000
    assert market.capLeverage() == 5000000000000000000
    assert market.circuitBreakerWindow() == 2592000
    assert market.circuitBreakerMintTarget() == 66670000000000000000000
    assert market.maintenanceMarginFraction() == 100000000000000000
    assert market.maintenanceMarginBurnRate() == 100000000000000000
    assert market.liquidationFeeRate() == 10000000000000000
    assert market.tradingFeeRate() == 750000000000000
    assert market.minCollateral() == 100000000000000
    assert market.priceDriftUpperLimit() == 100000000000000
