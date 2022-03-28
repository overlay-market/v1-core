import pytest
from brownie import RiskMock


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
def create_risk(alice):
    def create_risk():
        risk = alice.deploy(RiskMock)
        return risk
    yield create_risk


@pytest.fixture(scope="module")
def risk(create_risk):
    yield create_risk()
