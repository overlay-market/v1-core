import pytest
from brownie import (
    OverlayV1Factory, OverlayV1Market,
    OverlayV1Deployer, OverlayV1Token, OverlayV1FeedFactoryMock,
    web3
)


@pytest.fixture(scope="module")
def gov(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def charlie(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def rando(accounts):
    yield accounts[4]


@pytest.fixture(scope="module")
def fee_recipient(accounts):
    yield accounts[5]


@pytest.fixture(scope="module")
def guardian(accounts):
    yield accounts[6]


@pytest.fixture(scope="module")
def minter_role():
    yield web3.solidityKeccak(['string'], ["MINTER"])


@pytest.fixture(scope="module")
def burner_role():
    yield web3.solidityKeccak(['string'], ["BURNER"])


@pytest.fixture(scope="module")
def governor_role():
    yield web3.solidityKeccak(['string'], ["GOVERNOR"])


@pytest.fixture(scope="module")
def guardian_role():
    yield web3.solidityKeccak(['string'], ["GUARDIAN"])


@pytest.fixture(scope="module", params=[8000000])
def create_token(gov, alice, bob, minter_role, request):
    sup = request.param

    def create_token(supply=sup):
        tok = gov.deploy(OverlayV1Token)

        # mint the token then renounce minter role
        tok.grantRole(minter_role, gov, {"from": gov})
        tok.mint(gov, supply * 10 ** tok.decimals(), {"from": gov})
        tok.renounceRole(minter_role, gov, {"from": gov})

        tok.transfer(alice, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        tok.transfer(bob, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        return tok

    yield create_token


@pytest.fixture(scope="module")
def ovl(create_token):
    yield create_token()


@pytest.fixture(scope="module", params=[
    (600, 3600, 1000000000000000000, 1000000000000000000,
     2000000000000000000, 2000000000000000000, 3000000000000000000,
     3000000000000000000)
])
def create_feed_factory(gov, request, ovl):
    """
    Creates a new feed factory and deploys three mock feeds for testing.
    Below, third mock is used in creating a market for test_setters.py
    """
    (micro, macro, price_one, reserve_one, price_two,
     reserve_two, price_three, reserve_three) = request.param

    def create_feed_factory(tok=ovl, micro_window=micro, macro_window=macro,
                            mock_price_one=price_one,
                            mock_reserve_one=reserve_one,
                            mock_price_two=price_two,
                            mock_reserve_two=reserve_two,
                            mock_price_three=price_three,
                            mock_reserve_three=reserve_three):
        factory = gov.deploy(OverlayV1FeedFactoryMock, micro_window,
                             macro_window)

        # deploy the two feeds from the factory to add to registry
        factory.deployFeed(mock_price_one, mock_reserve_one)
        factory.deployFeed(mock_price_two, mock_reserve_two)
        factory.deployFeed(mock_price_three, mock_reserve_three)

        return factory

    yield create_feed_factory


@pytest.fixture(scope="module")
def feed_factory(create_feed_factory):
    yield create_feed_factory()


@pytest.fixture(scope="module")
def feed_one(feed_factory):
    feed = feed_factory.getFeed(1000000000000000000, 1000000000000000000)
    yield feed


@pytest.fixture(scope="module")
def feed_two(feed_factory):
    feed = feed_factory.getFeed(2000000000000000000, 2000000000000000000)
    yield feed


@pytest.fixture(scope="module")
def feed_three(feed_factory):
    feed = feed_factory.getFeed(3000000000000000000, 3000000000000000000)
    yield feed


@pytest.fixture(scope="module")
def create_factory(gov, guardian, fee_recipient, request, ovl, governor_role,
                   guardian_role, feed_factory, feed_three):

    def create_factory(tok=ovl, recipient=fee_recipient, feeds=feed_factory,
                       feed=feed_three):
        # create the market factory
        factory = gov.deploy(OverlayV1Factory, tok, recipient)

        # grant market factory token admin role
        tok.grantRole(tok.DEFAULT_ADMIN_ROLE(), factory, {"from": gov})

        # grant gov the governor role on token to access factory methods
        tok.grantRole(governor_role, gov, {"from": gov})
        # grant gov the guardian role on token to access factory methods
        tok.grantRole(guardian_role, guardian, {"from": gov})

        # add the feed factory
        factory.addFeedFactory(feeds, {"from": gov})

        # deploy a single market on feed three
        k = 1220000000000
        lmbda = 1000000000000000000
        delta = 2500000000000000
        cap_payoff = 5000000000000000000
        cap_notional = 800000000000000000000000
        cap_leverage = 2000000000000000000
        circuit_breaker_window = 2592000  # 30d
        circuit_breaker_mint_target = 66670000000000000000000  # 10% per year
        maintenance = 10000000000000000
        maintenance_burn = 100000000000000000
        liquidation_fee = 10000000000000000  # 1.00% (100 bps)
        trade_fee = 750000000000000
        min_collateral = 100000000000000
        price_drift_upper_limit = 10000000000000  # 0.001% per sec
        average_block_time = 14

        params = (k, lmbda, delta, cap_payoff, cap_notional, cap_leverage,
                  circuit_breaker_window, circuit_breaker_mint_target,
                  maintenance, maintenance_burn, liquidation_fee, trade_fee,
                  min_collateral, price_drift_upper_limit, average_block_time)
        _ = factory.deployMarket(feeds, feed, params, {"from": gov})

        return factory

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()


@pytest.fixture(scope="module")
def market(factory, feed_three):
    market_addr = factory.getMarket(feed_three)
    yield OverlayV1Market.at(market_addr)


@pytest.fixture(scope="module")
def deployer(factory):
    deployer_addr = factory.deployer()
    yield OverlayV1Deployer.at(deployer_addr)
