import pytest
from brownie import (
    Contract, OverlayV1UniswapV3Feed, OverlayV1NoReserveUniswapV3Feed
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


@pytest.fixture(scope="module", params=[(600, 3600, 200)])
def create_quanto_feed(gov, pool_daiweth_30bps, pool_uniweth_30bps,
                       dai, weth, uni, request):
    micro, macro, cardinality = request.param

    mkt_pool = pool_daiweth_30bps.address
    oe_pool = pool_uniweth_30bps.address
    tok = uni.address
    mkt_base_tok = weth.address
    mkt_quote_tok = dai.address
    mkt_base_amt = 1 * 10 ** weth.decimals()

    def create_quanto_feed(market_pool=mkt_pool, ovlweth_pool=oe_pool, ovl=tok,
                           market_base_token=mkt_base_tok,
                           market_quote_token=mkt_quote_tok,
                           market_base_amount=mkt_base_amt, micro_window=micro,
                           macro_window=macro, cardinality_min=cardinality):
        feed = gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                          market_base_token, market_quote_token,
                          market_base_amount, ovlweth_pool,
                          ovl, micro_window, macro_window,
                          cardinality_min, cardinality_min)
        return feed

    yield create_quanto_feed


@pytest.fixture(scope="module")
def quanto_feed(create_quanto_feed):
    yield create_quanto_feed()


@pytest.fixture(scope="module", params=[(600, 3600, 200)])
def create_quanto_feed_without_reserve(gov, pool_daiweth_30bps,
                                       pool_uniweth_30bps, dai, weth, request):
    micro, macro, cardinality = request.param

    mkt_pool = pool_daiweth_30bps.address
    mkt_base_tok = weth.address
    mkt_quote_tok = dai.address
    mkt_base_amt = 1 * 10 * weth.decimals()

    def create_quanto_feed_without_reserve(
          market_pool=mkt_pool,
          market_base_token=mkt_base_tok,
          market_quote_token=mkt_quote_tok,
          market_base_amount=mkt_base_amt,
          micro_window=micro, macro_window=macro,
          cardinality_min=cardinality):

        feed = gov.deploy(OverlayV1NoReserveUniswapV3Feed,
                          market_pool, market_base_token, market_quote_token,
                          market_base_amount, micro_window, macro_window,
                          cardinality_min)

        return feed

    yield create_quanto_feed_without_reserve


@pytest.fixture(scope="module")
def quanto_feed_without_reserve(create_quanto_feed_without_reserve):
    yield create_quanto_feed_without_reserve()


@pytest.fixture(scope="module", params=[(600, 3600, 200)])
def create_inverse_feed(gov, pool_uniweth_30bps, weth, uni, request):
    micro, macro, cardinality = request.param

    # treating uni as ovl for testing
    mkt_pool = pool_uniweth_30bps.address
    oe_pool = pool_uniweth_30bps.address
    tok = uni.address
    mkt_base_tok = weth.address
    mkt_quote_tok = uni.address
    mkt_base_amt = 1 * 10 ** uni.decimals()

    def create_inverse_feed(market_pool=mkt_pool, ovlweth_pool=oe_pool,
                            ovl=tok, market_base_token=mkt_base_tok,
                            market_quote_token=mkt_quote_tok,
                            market_base_amount=mkt_base_amt,
                            micro_window=micro, macro_window=macro,
                            cardinality_min=cardinality):
        feed = gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                          market_base_token, market_quote_token,
                          market_base_amount, ovlweth_pool,
                          ovl, micro_window, macro_window,
                          cardinality_min, cardinality_min)
        return feed

    yield create_inverse_feed


@pytest.fixture(scope="module")
def inverse_feed(create_inverse_feed):
    yield create_inverse_feed()
