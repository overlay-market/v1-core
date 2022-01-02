import pytest
from brownie import OverlayV1Factory, OverlayV1Token


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


@pytest.fixture(scope="module")
def create_factory(gov, request, ovl):

    def create_factory(tok=ovl):
        factory = gov.deploy(OverlayV1Factory, tok)
        tok.grantRole(tok.ADMIN_ROLE(), factory, {"from": gov})
        return factory

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()
