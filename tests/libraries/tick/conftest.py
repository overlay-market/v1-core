import pytest
from brownie import TickMock


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


@pytest.fixture(scope="module")
def create_tick_mock(alice):
    def create_tick_mock():
        tick_mock = alice.deploy(TickMock)
        return tick_mock
    yield create_tick_mock


@pytest.fixture(scope="module")
def tick_mock(create_tick_mock):
    yield create_tick_mock()
