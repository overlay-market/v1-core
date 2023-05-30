import pytest
from brownie import Contract, OverlayV1ChainlinkFeed, AggregatorMock


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
def chainlink_aggregator():
    # to be used as example aggregator
    yield Contract.from_explorer("0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419")


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
def create_chainlink_feed(gov, mock_aggregator, request):
    micro, macro = request.param
    aggregator_address = mock_aggregator.address

    def create_chainlink_feed(aggregator=aggregator_address,
                              micro_window=micro, macro_window=macro):
        feed = gov.deploy(OverlayV1ChainlinkFeed, aggregator,
                          micro_window, macro_window)
        return feed

    yield create_chainlink_feed


@pytest.fixture(scope="module")
def chainlink_feed(create_chainlink_feed):
    yield create_chainlink_feed()
