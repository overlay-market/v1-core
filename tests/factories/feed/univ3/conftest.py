import pytest
from brownie import (
    Contract, OverlayV1UniswapV3Factory, OverlayV1NoReserveUniswapV3Factory
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
def dai():
    yield Contract.from_explorer("0xda10009cbd5d07dd0cecc66161fc93d7c9000da1")


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_explorer("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")


@pytest.fixture(scope="module")
def uni():
    # to be used as example ovl
    yield Contract.from_explorer("0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0")


@pytest.fixture(scope="module")
def uni_factory():
    yield Contract.from_explorer("0x1F98431c8aD98523631AE4a59f267346ea31F984")


@pytest.fixture(scope="module")
def pool_daiweth_30bps():
    yield Contract.from_explorer("0x31Fa55e03bAD93C7f8AFfdd2eC616EbFde246001")


@pytest.fixture(scope="module")
def pool_uniweth_30bps():
    # to be used as example ovlweth pool
    yield Contract.from_explorer("0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801")


@pytest.fixture(scope="module", params=[(600, 1800, 240, 15)])
def create_factory_without_reserve(gov, uni_factory, weth, request):
    micro, macro, cardinality, block_time = request.param
    uni_fact = uni_factory.address

    def create_factory_without_reserve(
            univ3_factory=uni_fact,
            micro_window=micro, macro_window=macro,
            cardinality_min=cardinality,
            avg_block_time=block_time):
        factory = gov.deploy(
                        OverlayV1NoReserveUniswapV3Factory, univ3_factory,
                        micro_window, macro_window, cardinality_min,
                        avg_block_time)
        return factory

    yield create_factory_without_reserve


@pytest.fixture(scope="module")
def factory_without_reserve(create_factory_without_reserve):
    yield create_factory_without_reserve()


# TODO: change params to (600, 3600, 300, 14)
@pytest.fixture(scope="module", params=[(600, 1800, 240, 15)])
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
