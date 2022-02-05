import pytest
from brownie import Contract, OverlayV1BalancerV2Feed, reverts


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


def test_tt():
    assert 1 == 1


def test_deploy_feed_reverts_on_market_token_not_weth(gov, dai, usdc, bal,
                                                      pool_daiusdc_5bps,
                                                      pool_balweth_30bps):
    market_pool = pool_daiusdc_5bps
    ovlweth_pool = pool_balweth_30bps
    ovl = bal
    market_base_token = dai
    market_quote_token = usdc
    market_base_amount = 1000000000000000000
    micro_window = 600
    macro_window = 3600

    with reverts("OVLV1Feed: marketToken != WETH"):
        gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                   market_base_token, market_quote_token,
                   market_base_amount, micro_window, macro_window)
#
#
#  def test_deploy_feed_reverts_on_market_token_not_base(gov, weth,
#                                                        dai, rando, bal,
#                                                        pool_daiweth_30bps,
#                                                        pool_balweth_30bps):
#      market_pool = pool_daiweth_30bps
#      ovlweth_pool = pool_balweth_30bps
#      ovl = bal
#      market_base_token = rando
#      market_quote_token = weth
#      market_base_amount = 1000000
#      micro_window = 600
#      macro_window = 3600
#
#      with reverts("OVLV1Feed: marketToken != marketBaseToken"):
#          gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
#                     market_base_token, market_quote_token,
#                     market_base_amount, micro_window, macro_window)
#
#
#  def test_deploy_feed_reverts_on_market_token_not_quote(gov, dai, rando, bal,
#                                                         pool_daiweth_30bps,
#                                                         pool_balweth_30bps):
#      market_pool = pool_daiweth_30bps
#      ovlweth_pool = pool_balweth_30bps
#      ovl = bal
#      market_base_token = dai
#      market_quote_token = rando
#      market_base_amount = 1000000
#      micro_window = 600
#      macro_window = 3600
#
#      with reverts("OVLV1Feed: marketToken != marketQuoteToken"):
#          gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
#                     market_base_token, market_quote_token,
#                     market_base_amount, micro_window, macro_window)
#
#
#  def test_deploy_feed_reverts_on_weth_not_in_ovlweth_pool(gov, weth, dai,
#                                                           pool_daiweth_30bps,
#                                                           pool_daiusdc_5bps):
#      market_pool = pool_daiweth_30bps
#      ovlweth_pool = pool_daiusdc_5bps
#      ovl = dai
#      market_base_token = dai
#      market_quote_token = weth
#      market_base_amount = 1000000
#      micro_window = 600
#      macro_window = 3600
#
#      with reverts("OVLV1Feed: ovlWethToken != WETH"):
#          gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
#                     market_base_token, market_quote_token,
#                     market_base_amount, micro_window, macro_window)
#
#
#  def test_deploy_feed_reverts_on_ovl_not_in_ovlweth_pool(gov, weth, dai,
#                                                          pool_daiweth_30bps,
#                                                          pool_balweth_30bps):
#      market_pool = pool_daiweth_30bps
#      ovlweth_pool = pool_balweth_30bps
#      ovl = dai
#      market_base_token = dai
#      market_quote_token = weth
#      market_base_amount = 1000000
#      micro_window = 600
#      macro_window = 3600
#
#      with reverts("OVLV1Feed: ovlWethToken != OVL"):
#          gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
#                     market_base_token, market_quote_token,
#                     market_base_amount, micro_window, macro_window)
