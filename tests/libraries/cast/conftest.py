import pytest
from brownie import CastMock


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
def create_cast(alice):
    def create_cast():
        cast = alice.deploy(CastMock)
        return cast
    yield create_cast


@pytest.fixture(scope="module")
def cast(create_cast):
    yield create_cast()
