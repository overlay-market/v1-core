import pytest
from brownie import Contract, OverlayV1BalancerV2Feed


@pytest.fixture
def usdc():
    '''
    Returns the USDC token contract instance.

    https://etherscan.io/address/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
    '''
    yield Contract.from_explorer("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")


@pytest.fixture
def pool_daiusdc():
    '''
    Returns the DAI token contract instance used to simulate OVL for testing
    purposes.

    https://etherscan.io/address/0x6c6Bc977E13Df9b0de53b251522280BB72383700
    '''
    yield Contract.from_explorer("0x6c6Bc977E13Df9b0de53b251522280BB72383700")


@pytest.fixture
def feed(gov, dai, usdc, balancer, balv2_tokens, pool_daiusdc,
         pool_balweth):
    '''
    Returns the OverlayV1BalancerV2Feed contract instance. The market pool is
    BAL/WETH. For testing purposes, the DAI token is used to represent OVL.
    Inputs:
      gov      [EthAddress]: Governor role account address
      dai      [Contract]:   DAI token contract instance
      usdc     [Contract]:   USDC token contract instance
      balancer [Contract]:   BalancerGovernanceToken contract instance
      pool_daiusdc_5pbs [Contract]:   BalancerGovernanceToken contract instance
    '''
    # SN TODO: need setup function to reduce code duplication
    market_pool = pool_daiusdc
    ovlweth_pool = pool_balweth
    ovl = balancer
    market_base_token = dai
    market_quote_token = usdc
    market_base_amount = 1000000000000000000
    micro_window = 600
    macro_window = 3600

    # SN TODO: consider breaking up constructor logic -> see how impacts gas
    return gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                      market_base_token, market_quote_token,
                      market_base_amount, balv2_tokens, micro_window,
                      macro_window)


def test_get_pool_tokens(feed, balv2_tokens):
    '''
    Test that the getPoolTokens function defined in the IBalancerV2Vault
    interface returns the following when given a valid pool id:
        ( (token0 address, token1 address),
          (token0 balance, token1 balance),
           lastChangeBlock
        )
    SN TODO: Which token is which???
    token0 dai
    token1 weth
    '''
    tx_ovl = feed.getPoolTokensData(balv2_tokens[1])
    tx_bal = feed.getPoolTokensData(balv2_tokens[2])

    bal_address = '0xba100000625a3754423978a60c9317c58a424e3D'
    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    ovl_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F'  # DAI

    assert (tx_ovl[0][0] == bal_address)
    assert (tx_ovl[0][1] == weth_address)

    # for bal_weth_pool_id
    assert (tx_bal[0][0] == ovl_address)
    assert (tx_bal[0][1] == weth_address)
    #  assert (istype(tx[1]), tuple(int, int))
    #  assert (istype(tx[2]), int))
    #  assert (tx[2] > chain.now)


#  def test_deploy_feed_reverts_on_market_token_not_weth(gov, dai, usdc,
#                                                        balancer,
#                                                        balv2_tokens,
#                                                        pool_daiusdc,
#                                                        pool_balweth):
#      market_pool = pool_daiusdc
#      ovlweth_pool = pool_balweth
#      ovl = balancer
#      market_base_token = dai
#      market_quote_token = usdc
#      market_base_amount = 1000000000000000000
#      micro_window = 600
#      macro_window = 3600
#      print('balv2_tokens', balv2_tokens)
#      print()
#      print('balv2_tokens[2]', balv2_tokens[2]) # bal_weth_pool
#      feed = gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool,
#                 ovl, market_base_token, market_quote_token,
#                 market_base_amount, balv2_tokens, micro_window,
#                 macro_window)
#      print()
#      print()
#      print('feed', feed)
#      print()
#      print('feed', dir(feed))
#      print()
#      print()
#      tx = feed.getPoolTokensData(balv2_tokens[2])
#      print('tx = feed.getPoolTokensData(balv2_tokens[2])', tx)
#      print()
#  value = "0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014"
#      #  bal_id = brownie.convert.to_bytes(value, type_str="bytes32")
#      #  tx = feed.getPoolTokensData(bal_id)
#      #  print('TX', tx)
#      assert(1 == 1)

    #  with reverts("OVLV1Feed: marketToken != WETH"):
    #      gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
    #                 market_base_token, market_quote_token,
    #                 market_base_amount, balv2_tokens, micro_window,
    #                 macro_window)
#
#
#  def test_deploy_feed_reverts_on_market_token_not_base(gov, weth,
#                                                        dai, rando, bal,
#                                                        pool_daiweth,
#                                                        pool_balweth):
#      market_pool = pool_daiweth
#      ovlweth_pool = pool_balweth
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
#                                                         pool_daiweth,
#                                                         pool_balweth):
#      market_pool = pool_daiweth
#      ovlweth_pool = pool_balweth
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
#                                                           pool_daiweth,
#                                                           pool_daiusdc):
#      market_pool = pool_daiweth
#      ovlweth_pool = pool_daiusdc
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
#                                                          pool_daiweth,
#                                                          pool_balweth):
#      market_pool = pool_daiweth
#      ovlweth_pool = pool_balweth
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
