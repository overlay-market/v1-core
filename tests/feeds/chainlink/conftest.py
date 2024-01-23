import pytest
from brownie import ( 
    Contract, OverlayV1ChainlinkFeed, OverlayV1Token,
    AggregatorMock, web3
)


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
def chainlink_aggregator():
    # to be used as example aggregator (Arbitrum One)
    # corresponds to the feed 0x46b4143caf2fe2965349fca53730e83f91247e2c
    yield Contract.from_explorer("0x91F9C89891575C2E41edfFB5953565A9aE2Dbd9F")


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
def ov(create_token):
    yield create_token()


@pytest.fixture(scope="module")
def create_mock_aggregator(gov):
    # to be used as example aggregator
    def create_mock_aggregator():
        mock_aggregator = gov.deploy(AggregatorMock)
        return mock_aggregator

    yield create_mock_aggregator


@pytest.fixture(scope="module")
def mock_aggregator(create_mock_aggregator):
    # to be used as example aggregator
    yield create_mock_aggregator()


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_chainlink_feed(ov, gov, mock_aggregator, request):
    micro, macro = request.param
    aggregator_address = mock_aggregator.address

    def create_chainlink_feed(tok=ov, aggregator=aggregator_address,
                              micro_window=micro, macro_window=macro):
        feed = gov.deploy(OverlayV1ChainlinkFeed, tok, aggregator,
                          micro_window, macro_window, 3600)
        return feed

    yield create_chainlink_feed


@pytest.fixture(scope="module")
def chainlink_feed(create_chainlink_feed):
    yield create_chainlink_feed()
