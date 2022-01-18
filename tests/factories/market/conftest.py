import pytest
from brownie import (
    interface, OverlayV1Factory, OverlayV1Token, OverlayV1FeedFactoryMock
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


@pytest.fixture(scope="module", params=[8000000])
def create_token(gov, alice, bob, request):
    sup = request.param

    def create_token(supply=sup):
        tok = gov.deploy(OverlayV1Token)
        tok.mint(gov, supply * 10 ** tok.decimals(), {"from": gov})
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
def create_factory(gov, request, ovl, feed_factory, feed_three):

    def create_factory(tok=ovl, feeds=feed_factory, feed=feed_three):
        # create the market factory
        factory = gov.deploy(OverlayV1Factory, tok)

        # grant market factory token admin role
        tok.grantRole(tok.ADMIN_ROLE(), factory, {"from": gov})

        # add the feed factory
        factory.addFeedFactory(feeds, {"from": gov})

        # deploy a single market on feed three
        k = 1220000000000
        lmbda = 1000000000000000000
        delta = 2500000000000000
        cap_payoff = 5000000000000000000
        cap_oi = 800000000000000000000000
        cap_leverage = 5000000000000000000
        maintenance = 100000000000000000
        maintenance_burn = 100000000000000000
        trade_fee = 750000000000000
        min_collateral = 100000000000000
        _ = factory.deployMarket(feeds, feed, k, lmbda, delta,
                                 cap_payoff, cap_oi, cap_leverage,
                                 maintenance, maintenance_burn, trade_fee,
                                 min_collateral, {"from": gov})

        return factory

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()


@pytest.fixture(scope="module")
def market(factory, feed_three):
    market_addr = factory.getMarket(feed_three)
    yield interface.IOverlayV1Market(market_addr)