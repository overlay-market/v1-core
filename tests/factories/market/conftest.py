import pytest
from brownie import OverlayV1Factory, OverlayV1Token, OverlayV1FeedFactoryMock


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


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_feed_factory(gov, request, ovl):
    micro, macro = request.param

    def create_feed_factory(tok=ovl, micro_window=micro, macro_window=macro):
        factory = gov.deploy(OverlayV1FeedFactoryMock, micro_window,
                             macro_window)
        return factory

    yield create_feed_factory


@pytest.fixture(scope="module")
def feed_factory(create_feed_factory):
    yield create_feed_factory()


@pytest.fixture(scope="module")
def create_factory(gov, request, ovl, feed_factory):

    def create_factory(tok=ovl, feeds=feed_factory):
        factory = gov.deploy(OverlayV1Factory, tok)
        tok.grantRole(tok.ADMIN_ROLE(), factory, {"from": gov})
        factory.addFeedFactory(feeds.address, {"from": gov})
        return factory

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()
