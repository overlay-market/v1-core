import pytest
from brownie import RollerMock


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
def create_roller(alice):
    def create_roller():
        roller = alice.deploy(RollerMock)
        return roller
    yield create_roller


@pytest.fixture(scope="module")
def roller(create_roller):
    yield create_roller()
