def test_factory_fixture(factory, fee_recipient, feed_factory, feed_three, ovl,
                         gov, market, deployer, governor_role):
    # check ovl immutable set
    assert factory.ovl() == ovl

    # check fee recipient set
    assert factory.feeRecipient() == fee_recipient

    # check deployer contract deployed on factory deploy
    assert factory.deployer() != "0x0000000000000000000000000000000000000000"
    assert deployer.factory() == factory

    # check factory has been given admin role on ovl token
    assert ovl.hasRole(ovl.DEFAULT_ADMIN_ROLE(), factory) is True

    # check gov has been given governance role on ovl token
    assert ovl.hasRole(governor_role, gov) is True

    # check feed factory has been added to registry
    assert factory.isFeedFactory(feed_factory) is True

    # check market deployed for feed three has been added to registry
    assert factory.getMarket(feed_three) == market
    assert factory.isMarket(market) is True

    # check min param bounds
    expect_params_min = [
        400000000,  # MIN_K = ~ 0.1 bps / 8 hr
        10000000000000000,  # MIN_LMBDA = 0.01
        100000000000000,  # MIN_DELTA = 0.01% (1 bps)
        1000000000000000000,  # MIN_CAP_PAYOFF = 1x
        0,  # MIN_CAP_NOTIONAL = 0 OVL
        1000000000000000000,  # MIN_CAP_LEVERAGE= 1x
        86400,  # MIN_CIRCUIT_BREAKER_WINDOW= 1 day
        0,  # MIN_CIRCUIT_BREAKER_MINT_TARGET= 0 OVL
        10000000000000000,  # MIN_MAINTENANCE_MARGIN_FRACTION = 1 %
        10000000000000000,  # MIN_MAINTENANCE_MARGIN_BURN_RATE = 1 %
        1000000000000000,  # MIN_LIQUIDATION_FEE_RATE = 0.10 % (10 bps)
        100000000000000,  # MIN_TRADING_FEE_RATE = 0.01 % (1 bps)
        1000000000000,  # MIN_MINIMUM_COLLATERAL= 1e-6 OVL
        1000000000000,  # MIN_PRICE_DRIFT_UPPER_LIMIT= 0.01 bps/s
        0  # MIN_AVERAGE_BLOCK_TIME = 0s
    ]
    actual_params_min = [
        factory.PARAMS_MIN(i) for i in range(len(expect_params_min))
    ]
    assert expect_params_min == actual_params_min

    # check max param bounds
    expect_params_max = [
        4000000000000,  # MAX_K = ~ 1000 bps / 8 hr
        10000000000000000000,  # MAX_LMBDA = 10
        20000000000000000,  # MAX_DELTA = 2% (200 bps)
        100000000000000000000,  # MAX_CAP_PAYOFF = 100x
        # MAX_CAP_NOTIONAL = 8,000,000 OVL (initial supply)
        8000000000000000000000000,
        20000000000000000000,  # MAX_CAP_LEVERAGE = 20x
        31536000,  # MAX_CIRCUIT_BREAKER_WINDOW = 365 days
        # MAX_CIRCUIT_BREAKER_MINT_TARGET = 8,000,000 OVL
        8000000000000000000000000,
        200000000000000000,  # MAX_MAINTENANCE_MARGIN_FRACTION = 20%
        500000000000000000,  # MAX_MAINTENANCE_MARGIN_BURN_RATE = 50%
        200000000000000000,  # MAX_LIQUIDATION_FEE_RATE = 20.00% (1000 bps)
        5000000000000000,  # MAX_TRADING_FEE_RATE = 0.50% (50 bps)
        1000000000000000000,  # MAX_MINIMUM_COLLATERAL = 1 OVL
        100000000000000,  # MAX_PRICE_DRIFT_UPPER_LIMIT = 1 bps/s
        3600  # MAX_AVERAGE_BLOCK_TIME = 1h
    ]
    actual_params_max = [
        factory.PARAMS_MAX(i) for i in range(len(expect_params_max))
    ]
    assert expect_params_max == actual_params_max


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

    expect_params = [
        1220000000000,
        1000000000000000000,
        2500000000000000,
        5000000000000000000,
        800000000000000000000000,
        2000000000000000000,
        2592000,
        66670000000000000000000,
        10000000000000000,
        100000000000000000,
        10000000000000000,
        750000000000000,
        100000000000000,
        10000000000000,
        14
    ]
    actual_params = [market.params(i) for i in range(15)]
    assert expect_params == actual_params
