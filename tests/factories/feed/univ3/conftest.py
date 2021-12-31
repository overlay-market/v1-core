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
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def uni():
    # to be used as example ovl
    yield Contract.from_explorer("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")


@pytest.fixture(scope="module")
def pool_daiweth_30bps():
    yield Contract.from_explorer("0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")


@pytest.fixture(scope="module")
def pool_uniweth_30bps():
    # to be used as example ovlweth pool
    yield Contract.from_explorer("0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801")


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_factory(gov, pool_uniweth_30bps, weth, uni, request):
    micro, macro = request.param
    oe_pool = pool_uniweth_30bps.address
    tok = uni.address

    def create_factory(ovlweth_pool=oe_pool, ovl=tok, micro_window=micro,
                       macro_window=macro):
        feed = gov.deploy(OverlayV1UniswapV3Factory, ovlweth_pool, ovl,
                          micro_window, macro_window)
        return feed

    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()
