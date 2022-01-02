import pytest
from brownie import OverlayV1FeedFactoryMock


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


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_factory(gov, request):
    micro, macro = request.param

    def create_factory(micro_window=micro, macro_window=macro):
        factory = gov.deploy(OverlayV1FeedFactoryMock, micro_window,
                             macro_window)
        return factory

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()
