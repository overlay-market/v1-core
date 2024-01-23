from .utils import RiskParameter


def test_ov_fixture(ov):
    assert ov.decimals() == 18
    assert ov.name() == "Overlay"
    assert ov.symbol() == "OV"
    assert ov.totalSupply() == 8000000000000000000000000


def test_token_fixtures(uni):
    assert uni.name() == "Uniswap"


def test_factory_fixture(factory, ov, fee_recipient):
    assert factory.ov() == ov
    assert factory.feeRecipient() == fee_recipient


def test_feed_fixture(feed):
    assert feed.microWindow() == 600
    assert feed.macroWindow() == 3600


def test_mock_feed_fixture(mock_feed):
    assert mock_feed.microWindow() == 600
    assert mock_feed.macroWindow() == 1800
    assert mock_feed.price() == 1000000000000000000
    assert mock_feed.reserve() == 2000000000000000000000000


def test_fake_feed_fixture(fake_feed):
    assert fake_feed.microWindow() == 600
    assert fake_feed.macroWindow() == 1800
    assert fake_feed.price() == 1000000000000000000
    assert fake_feed.reserve() == 2000000000000000000000000


def test_fake_deployer_fixture(fake_deployer, fake_factory, ov):
    assert fake_deployer.factory() == fake_factory
    assert fake_deployer.ov() == ov

    tok, feed, fact = fake_deployer.parameters()
    assert tok == ov
    assert feed == "0x0000000000000000000000000000000000000000"
    assert fact == fake_factory


def test_mock_market_fixture(mock_market, mock_feed, ov, factory,
                             minter_role, burner_role, gov):
    # check addresses set properly
    assert mock_market.ov() == ov
    assert mock_market.feed() == mock_feed
    assert mock_market.factory() == factory

    # risk params
    expect_params = [
        122000000000,
        500000000000000000,
        2500000000000000,
        5000000000000000000,
        800000000000000000000000,
        5000000000000000000,
        2592000,
        66670000000000000000000,
        100000000000000000,
        100000000000000000,
        50000000000000000,
        750000000000000,
        100000000000000,
        25000000000000,
        250
    ]
    actual_params = [mock_market.params(name.value) for name in RiskParameter]
    assert expect_params == actual_params

    # check mock market has minter and burner roles on ov token
    assert ov.hasRole(minter_role, mock_market) is True
    assert ov.hasRole(burner_role, mock_market) is True

    # check oi related quantities are zero
    assert mock_market.oiLong() == 0
    assert mock_market.oiShort() == 0
    assert mock_market.oiLongShares() == 0
    assert mock_market.oiShortShares() == 0

    # check is shutdown set to false
    assert mock_market.isShutdown() is False

    # check timestamp update last is same as block when mock_market deployed
    # NOTE: -3 in index since had two grantRole txs after in conftest.py
    assert mock_market.timestampUpdateLast() != 0


def test_market_fixture(market, feed, ov, factory, minter_role,
                        burner_role, gov):
    # check addresses set properly
    assert market.ov() == ov
    assert market.feed() == feed
    assert market.factory() == factory

    # risk params
    expect_params = [
        122000000000,
        500000000000000000,
        2500000000000000,
        5000000000000000000,
        800000000000000000000000,
        5000000000000000000,
        2592000,
        66670000000000000000000,
        100000000000000000,
        100000000000000000,
        50000000000000000,
        750000000000000,
        100000000000000,
        25000000000000,
        250
    ]
    actual_params = [market.params(name.value) for name in RiskParameter]
    assert expect_params == actual_params

    # check market has minter and burner roles on ov token
    assert ov.hasRole(minter_role, market) is True
    assert ov.hasRole(burner_role, market) is True

    # check oi related quantities are zero
    assert market.oiLong() == 0
    assert market.oiShort() == 0
    assert market.oiLongShares() == 0
    assert market.oiShortShares() == 0

    # check is shutdown set to false
    assert market.isShutdown() is False

    # check timestamp update last is same as block when market was deployed
    # NOTE: -3 in index since had two grantRole txs after in conftest.py
    assert market.timestampUpdateLast() != 0
