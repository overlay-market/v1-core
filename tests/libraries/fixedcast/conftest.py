import pytest
from brownie import FixedCastMock


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
def create_fixed_cast(alice):
    def create_fixed_cast():
        fixed_cast = alice.deploy(FixedCastMock)
        return fixed_cast
    yield create_fixed_cast


@pytest.fixture(scope="module")
def fixed_cast(create_fixed_cast):
    yield create_fixed_cast()
