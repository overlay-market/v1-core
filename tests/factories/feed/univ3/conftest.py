import pytest
from brownie import Contract, OverlayV1UniswapV3Factory


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
def dai():
    '''
    Returns the DAI token contract instance used to simulate OVL for testing
    purposes.

    https://etherscan.io/address/0x6B175474E89094C44Da98b954EedeAC495271d0F
    '''
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    '''
    Returns the Wrapped Ether (WETH) token contract instance.

    https://etherscan.io/address/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
    '''
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def uni():
    '''
    Returns the Uniswap V3 Uni token contract instance.

    https://etherscan.io/address/0xba100000625a3754423978a60c9317c58a424e3D
    '''
    # to be used as example ovl
    yield Contract.from_explorer("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")


@pytest.fixture(scope="module")
def uni_factory():
    yield Contract.from_explorer("0x1F98431c8aD98523631AE4a59f267346ea31F984")


@pytest.fixture(scope="module")
def pool_daiweth_30bps():
    '''
    Returns the Uniswap V3 DAI/ETH pool contract instance.

    https://etherscan.io/address/0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8
    https://info.uniswap.org/#/pools/0xc2e9f25be6257c210d7adf0d4cd6e3e881ba25f8
    '''
    yield Contract.from_explorer("0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")


@pytest.fixture(scope="module")
def pool_uniweth_30bps():
    '''
    Returns the Uniswap V3 UNI/ETH pool contract instance, intended to be used
    as an example OVL/WETH pool.

    https://etherscan.io/address/0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801
    https://info.uniswap.org/#/pools/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801
    '''
    yield Contract.from_explorer("0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801")


# TODO: change params to (600, 3600, 300, 14)
@pytest.fixture(scope="module", params=[(600, 3000, 200, 15)])
def create_factory(gov, uni_factory, weth, uni, request):
    micro, macro, cardinality, block_time = request.param
    uni_fact = uni_factory.address
    tok = uni.address

    def create_factory(univ3_factory=uni_fact, ovl=tok, micro_window=micro,
                       macro_window=macro, cardinality_min=cardinality,
                       avg_block_time=block_time):
        factory = gov.deploy(OverlayV1UniswapV3Factory, ovl, univ3_factory,
                             micro_window, macro_window, cardinality_min,
                             avg_block_time)
        return factory

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()
