import pytest
from brownie import PositionMock


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
def create_position(alice):
    def create_position():
        position = alice.deploy(PositionMock)
        return position
    yield create_position


@pytest.fixture(scope="module")
def position(create_position):
    yield create_position()
