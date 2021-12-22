import pytest
from brownie import OverlayV1QuadraticFeedMock


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
def rando(accounts):
    yield accounts[3]


@pytest.fixture(scope="module", params=[(600, 3600, 1, 2)])
def create_feed(gov, request):
    micro, macro, m_p, m_r = request.param

    def create_feed(micro_window=micro, macro_window=macro, m_price=m_p, m_reserve=m_r):
        feed = gov.deploy(OverlayV1QuadraticFeedMock, micro_window, macro_window, m_price, m_reserve)
        return feed

    yield create_feed


@pytest.fixture(scope="module")
def feed(create_feed):
    yield create_feed()
