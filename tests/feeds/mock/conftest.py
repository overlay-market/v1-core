import pytest
from brownie import OverlayV1FeedMock


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


@pytest.fixture(scope="module", params=[
    (600, 3600, 1000000000000000000, 2000000000000000000000000)
])
def create_feed(gov, request):
    micro, macro, p, r = request.param

    def create_feed(micro_window=micro, macro_window=macro,
                    price=p, reserve=r):
        feed = gov.deploy(OverlayV1FeedMock, micro_window, macro_window,
                          price, reserve)
        return feed

    yield create_feed


@pytest.fixture(scope="module")
def feed(create_feed):
    yield create_feed()
