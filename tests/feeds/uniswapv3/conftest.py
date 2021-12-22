import pytest
from brownie import Contract, OverlayV1Token, OverlayV1UniswapV3Feed


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
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def ens():
    yield Contract.from_explorer("0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72")


@pytest.fixture(scope="module")
def pool_daiweth_30bps():
    yield Contract.from_explorer("0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")


@pytest.fixture(scope="module")
def pool_ensweth_30bps():
    # to be used as example ovlweth pool
    yield Contract.from_explorer("0x92560C178cE069CC014138eD3C2F5221Ba71f58a")


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
def token(create_token):
    yield create_token()


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_quanto_feed(gov, token, pool_daiweth_30bps, pool_ensweth_30bps,
                       dai, weth, ens, request):
    micro, macro, p, r = request.param

    mkt_pool = pool_daiweth_30bps.address()
    oe_pool = pool_ensweth_30bps.address()
    tok = token.address()
    mkt_base_tok = weth.address()
    mkt_quote_tok = dai.address()
    mkt_base_amt = 1 * 10 ** weth.decimals()

    def create_feed(market_pool=mkt_pool, ovlweth_pool=oe_pool, ovl=tok,
                    market_base_token=mkt_base_tok,
                    market_quote_token=mkt_quote_tok,
                    market_base_amount=mkt_base_amt, micro_window=micro,
                    macro_window=macro):
        feed = gov.deploy(OverlayV1UniswapV3Feed, market_pool, ovlweth_pool,
                          ovl, market_base_token, market_quote_token,
                          market_base_amount, micro_window, macro_window)
        return feed

    yield create_feed


@pytest.fixture(scope="module")
def quanto_feed(create_quanto_feed):
    yield create_quanto_feed()


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_inverse_feed(gov, token, pool_ensweth_30bps, weth, ens, request):
    micro, macro, p, r = request.param

    mkt_pool = pool_ensweth_30bps.address()
    oe_pool = pool_ensweth_30bps.address()
    tok = token.address()
    mkt_base_tok = weth.address()
    mkt_quote_tok = ens.address()
    mkt_base_amt = 1 * 10 ** ens.decimals()

    def create_feed(market_pool=mkt_pool, ovlweth_pool=oe_pool, ovl=tok,
                    market_base_token=mkt_base_tok,
                    market_quote_token=mkt_quote_tok,
                    market_base_amount=mkt_base_amt, micro_window=micro,
                    macro_window=macro):
        feed = gov.deploy(OverlayV1UniswapV3Feed, market_pool, ovlweth_pool,
                          ovl, market_base_token, market_quote_token,
                          market_base_amount, micro_window, macro_window)
        return feed

    yield create_feed


@pytest.fixture(scope="module")
def inverse_feed(create_inverse_feed):
    yield create_quanto_feed()
