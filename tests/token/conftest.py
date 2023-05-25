import pytest
from brownie import OverlayV1Token, web3


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
def minter_role():
    yield web3.solidityKeccak(['string'], ["MINTER"])


@pytest.fixture(scope="module")
def burner_role():
    yield web3.solidityKeccak(['string'], ["BURNER"])


@pytest.fixture(scope="module")
def governor_role():
    yield web3.solidityKeccak(['string'], ["GOVERNOR"])


@pytest.fixture(scope="module")
def guardian_role():
    yield web3.solidityKeccak(['string'], ["GUARDIAN"])


@pytest.fixture(scope="module", params=[8000000])
def create_token(gov, alice, bob, minter_role, request):
    sup = request.param

    def create_token(supply=sup):
        tok = gov.deploy(OverlayV1Token)

        # mint the token then renounce minter role
        tok.grantRole(minter_role, gov, {"from": gov})
        tok.mint(gov, supply * 10 ** tok.decimals(), {"from": gov})
        tok.renounceRole(minter_role, gov, {"from": gov})

        tok.transfer(alice, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        tok.transfer(bob, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        return tok

    yield create_token


@pytest.fixture(scope="module")
def token(create_token):
    yield create_token()


@pytest.fixture(scope="module")
def create_minter(token, gov, accounts, minter_role):
    def create_minter(tok=token, governance=gov):
        tok.grantRole(minter_role, accounts[4], {"from": gov})
        return accounts[4]

    yield create_minter


@pytest.fixture(scope="module")
def minter(create_minter):
    yield create_minter()


@pytest.fixture(scope="module")
def create_burner(token, gov, accounts, burner_role):
    def create_burner(tok=token, governance=gov):
        tok.grantRole(burner_role, accounts[5], {"from": gov})
        return accounts[5]

    yield create_burner


@pytest.fixture(scope="module")
def burner(create_burner):
    yield create_burner()


@pytest.fixture(scope="module")
def create_governor(token, gov, accounts, governor_role):
    def create_governor(tok=token, governance=gov):
        tok.grantRole(governor_role, accounts[6], {"from": gov})
        return accounts[6]

    yield create_governor


@pytest.fixture(scope="module")
def create_guardian(token, gov, accounts, guardian_role):
    def create_guardian(tok=token, governance=gov):
        tok.grantRole(guardian_role, accounts[7], {"from": gov})
        return accounts[7]

    yield create_guardian


@pytest.fixture(scope="module")
def governor(create_governor):
    yield create_governor()


@pytest.fixture(scope="module")
def guardian(create_guardian):
    yield create_guardian()


@pytest.fixture(scope="module")
def create_admin(token, gov, accounts):
    def create_admin(tok=token, governance=gov):
        tok.grantRole(tok.DEFAULT_ADMIN_ROLE(), accounts[7], {"from": gov})
        return accounts[7]

    yield create_admin


@pytest.fixture(scope="module")
def admin(create_admin):
    yield create_admin()


@pytest.fixture(scope="module")
def create_market(token, admin, accounts, minter_role, burner_role):
    def create_market(tok=token, adm=admin):
        tok.grantRole(minter_role, accounts[8], {"from": adm})
        tok.grantRole(burner_role, accounts[8], {"from": adm})
        return accounts[8]

    yield create_market


@pytest.fixture(scope="module")
def market(create_market):
    yield create_market()
