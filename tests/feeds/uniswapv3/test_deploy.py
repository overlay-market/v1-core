import pytest
from brownie import Contract, OverlayV1UniswapV3Feed, reverts


@pytest.fixture
def usdc():
    '''
    Returns the USDC token contract instance.

    https://etherscan.io/address/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
    '''
    yield Contract.from_explorer("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")


@pytest.fixture
def pool_daiusdc_5bps():
    '''
    Returns the DAI token contract instance used to simulate OVL for testing
    purposes.

    https://etherscan.io/address/0x6c6Bc977E13Df9b0de53b251522280BB72383700
    '''
    yield Contract.from_explorer("0x6c6Bc977E13Df9b0de53b251522280BB72383700")


def test_deploy_feed_reverts_on_market_token_not_weth(gov, dai, usdc, uni,
                                                      pool_daiusdc_5bps,
                                                      pool_uniweth_30bps):
    market_pool = pool_daiusdc_5bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = dai
    market_quote_token = usdc
    market_base_amount = 1000000000000000000
    micro_window = 600
    macro_window = 3600
    cardinality = 200

    with reverts("OVLV1: marketToken != X"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window, cardinality, cardinality)


def test_deploy_feed_reverts_on_market_token_not_base(gov, weth,
                                                      dai, rando, uni,
                                                      pool_daiweth_30bps,
                                                      pool_uniweth_30bps):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = rando
    market_quote_token = weth
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600
    cardinality = 200

    with reverts("OVLV1: marketToken != marketBaseToken"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window, cardinality, cardinality)


def test_deploy_feed_reverts_on_market_token_not_quote(gov, dai, rando, uni,
                                                       pool_daiweth_30bps,
                                                       pool_uniweth_30bps):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = dai
    market_quote_token = rando
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600
    cardinality = 200

    with reverts("OVLV1: marketToken != marketQuoteToken"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window, cardinality, cardinality)


def test_deploy_feed_reverts_on_weth_not_in_ovlweth_pool(gov, weth, dai,
                                                         pool_daiweth_30bps,
                                                         pool_daiusdc_5bps):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_daiusdc_5bps
    ovl = dai
    market_base_token = dai
    market_quote_token = weth
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600
    cardinality = 200

    with reverts("OVLV1: marketToken != X"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window, cardinality, cardinality)


def test_deploy_feed_reverts_on_ovl_not_in_ovlweth_pool(gov, weth, dai,
                                                        pool_daiweth_30bps,
                                                        pool_uniweth_30bps):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = dai
    market_base_token = dai
    market_quote_token = weth
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600
    cardinality = 200

    with reverts("OVLV1: ovlXToken != OVL"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window, cardinality, cardinality)


def test_deploy_feed_reverts_on_cardinal_in_market_pool(gov, weth, dai, uni,
                                                        pool_daiweth_30bps,
                                                        pool_uniweth_30bps):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600

    # TODO: fix so not hardcoded
    cardinality_market = 400
    cardinality_ovlweth = 300

    with reverts("OVLV1: marketCardinality < min"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window,
                   cardinality_market, cardinality_ovlweth)


def test_deploy_feed_reverts_on_cardinal_in_ovlweth_pool(gov, weth, dai, uni,
                                                         pool_daiweth_30bps,
                                                         pool_uniweth_30bps):
    market_pool = pool_daiweth_30bps
    ovlweth_pool = pool_uniweth_30bps
    ovl = uni
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600

    # TODO: fix so not hardcoded
    cardinality_market = 200
    cardinality_ovlweth = 400

    with reverts("OVLV1: ovlXCardinality < min"):
        gov.deploy(OverlayV1UniswapV3Feed, market_pool,
                   market_base_token, market_quote_token,
                   market_base_amount, ovlweth_pool, ovl,
                   micro_window, macro_window,
                   cardinality_market, cardinality_ovlweth)
