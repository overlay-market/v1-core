import pytest
from brownie import Contract, reverts, OverlayV1BalancerV2Feed


@pytest.fixture
def usdc():
    '''
    Returns the USDC token contract instance.

    https://etherscan.io/address/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
    '''
    yield Contract.from_explorer("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")


@pytest.fixture
def par():
    '''
    Returns the PAR token contract instance used for testing the require
    statements of the OverlayV1BalancerV2Feed contract constructor function.

    https://etherscan.io/address/0x68037790A0229e9Ce6EaA8A99ea92964106C4703
    '''
    yield Contract.from_explorer("0x68037790A0229e9Ce6EaA8A99ea92964106C4703")


@pytest.fixture
def pool_usdcbal():
    '''
    Returns the Balancer V2 WeightedPool2Tokens USDC/BAL contract instance.

    https://app.balancer.fi/#/pool/0x9c08c7a7a89cfd671c79eacdc6f07c1996277ed5000200000000000000000025  # noqa: E501
    '''
    yield Contract.from_explorer("0x9c08C7a7a89cfD671c79eacdc6F07c1996277eD5")


def test_deploy_feed_reverts_on_market_token_not_weth(gov, balancer, par, usdc,
                                                      pool_parusdc,
                                                      pool_balweth,
                                                      balv2_tokens,
                                                      parusdc_poolid):
    '''
    Tests that the OverlayV1BalancerV2Feed contract deploy function reverts
    when the market token pair does NOT include WETH. To generate the expected
    failure, the market token pair must not contain WETH. The PAR/USDC pool is
    used to simulate this failing market token pair.

    Inputs:
      gov             [Account]:  Governor role account deploys the
                                  OverlayV1BalancerV2Feed contract
      balancer        [Contract]: BAL token contract instance representing the
                                  OVL token
      usdc            [Contract]: USDC token contract instance representing the
                                  market quote token
      par             [Contract]: PAR token contract instance representing the
                                  market base token
      pool_parusdc    [Contract]: PAR/USDC Balancer V2 WeightedPool2Tokens
                                  contract instance representing the market
                                  token pair
      pool_balweth    [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                                  contract instance representing the OVL/WETH
                                  token pair
     parusdc_poolid [bytes32]:  PAR/USDC Balancer V2 pool id
    '''
    # Market token pair does NOT contain WETH which causes the constructor to
    # revert
    market_pool = pool_parusdc
    ovlweth_pool = pool_balweth
    ovl = balancer
    market_base_token = par
    market_quote_token = usdc
    market_base_amount = 1000000000000000000
    micro_window = 600
    macro_window = 3600

    # Set the BalancerV2Tokens marketPoolId field to the PAR/USDC pool id to
    # trigger the expected failure.
    balv2_tokens = (balv2_tokens[0], balv2_tokens[1], parusdc_poolid)

    with reverts("OVLV1Feed: marketToken != WETH"):
        gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                   market_base_token, market_quote_token,
                   market_base_amount, balv2_tokens, micro_window,
                   macro_window)

#  def test_reverts_on_balancer_pool_id_mismatch():
#      # SN TODO


def test_deploy_feed_reverts_on_market_token_not_base(gov, weth, rando,
                                                      balancer, balv2_tokens,
                                                      pool_daiweth,
                                                      pool_balweth):
    '''
    Tests that the OverlayV1BalancerV2Feed contract deploy function reverts
    when the market token pair does NOT include the market base token.

    To generate the expected failure, the DAI/WETH market token pair must not
    contain the market base token. The market base token is defined as a random
    address instead of WETH.

    Inputs:
      gov          [Account]:  Governor role account deploys the
                               OverlayV1BalancerV2Feed contract
      weth         [Contract]: WETH token contract instance
      rando        [Account]:  Random eth address representing the market base
                               token causing the expected failure
      balancer     [Contract]: BAL token contract instance representing the OVL
                               token
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
      pool_daiweth [Contract]: PAR/USDC Balancer V2 WeightedPool2Tokens
                               contract instance representing the market token
                               pair
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
    '''
    market_pool = pool_daiweth
    ovlweth_pool = pool_balweth
    ovl = balancer
    market_base_token = rando
    market_quote_token = weth
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600

    with reverts("OVLV1Feed: marketToken != marketBaseToken"):
        gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                   market_base_token, market_quote_token, market_base_amount,
                   balv2_tokens, micro_window, macro_window)


def test_deploy_feed_reverts_on_market_token_not_quote(gov, rando, dai,
                                                       balancer, balv2_tokens,
                                                       pool_daiweth,
                                                       pool_balweth):
    '''
    Tests that the OverlayV1BalancerV2Feed contract deploy function reverts
    when the market token pair does NOT include the market quote token.

    To generate the expected failure, the DAI/WETH market token pair must not
    contain the market quote token. The market quote token is defined as a
    random address instead of WETH.

    Inputs:
      gov          [Account]:  Governor role account deploys the
                               OverlayV1BalancerV2Feed contract
      rando        [Account]:  Random eth address representing the market quote
                               token causing the expected failure
      balancer     [Contract]: BAL token contract instance representing the OVL
                               token
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
      pool_daiweth [Contract]: PAR/USDC Balancer V2 WeightedPool2Tokens
                               contract instance representing the market token
                               pair
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
    '''
    market_pool = pool_daiweth
    ovlweth_pool = pool_balweth
    ovl = balancer
    market_base_token = dai
    market_quote_token = rando
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600

    with reverts("OVLV1Feed: marketToken != marketQuoteToken"):
        gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                   market_base_token, market_quote_token,
                   market_base_amount, balv2_tokens, micro_window,
                   macro_window)


def test_deploy_feed_reverts_on_weth_not_in_ovlweth_pool(gov, weth, dai, par,
                                                         balv2_tokens,
                                                         parusdc_poolid,
                                                         pool_daiweth,
                                                         pool_parusdc):
    '''
    Tests that the OverlayV1BalancerV2Feed contract deploy function reverts
    when the OVL/WETH token pair does NOT include WETH.

    To generate the expected failure, the OVL/WETH token pair must not contain
    the WETH token and the PAR/USDC is used instead.

    Inputs:
      gov          [Account]:  Governor role account deploys the
                               OverlayV1BalancerV2Feed contract
      weth         [Contract]: WETH token contract instance
      dai          [Contract]: DAI token contract instance
      par          [Contract]: PAR token contract instance representing the OVL
                               token
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
      pool_daiweth [Contract]: PAR/USDC Balancer V2 WeightedPool2Tokens
                               contract instance representing the market token
                               pair
      pool_parusdc [Contract]: PAR/USDC Balancer V2 WeightedPool2Tokens
                               contract instance representing the market token
                               pair
    '''
    market_pool = pool_daiweth
    ovlweth_pool = pool_parusdc
    ovl = par
    market_base_token = dai
    market_quote_token = weth
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600

    # Set the BalancerV2Tokens ovlWethPoolId field to the PAR/USDC pool id to
    # trigger the expected failure.
    balv2_tokens = (balv2_tokens[0], parusdc_poolid, balv2_tokens[2])

    with reverts("OVLV1Feed: ovlWethToken != WETH"):
        gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                   market_base_token, market_quote_token,
                   market_base_amount, balv2_tokens, micro_window,
                   macro_window)


def test_deploy_feed_reverts_on_ovl_not_in_ovlweth_pool(gov, weth, dai,
                                                        balv2_tokens,
                                                        balweth_poolid,
                                                        pool_daiweth,
                                                        pool_balweth):
    '''
    Tests that the OverlayV1BalancerV2Feed contract deploy function reverts
    when the OVL/WETH token pair does NOT include OVL.

    The OVL/WETH token pair is represented by BAL/WETH for testing purposes,
    therefore, to generate the expected failure, the BAL/WETH token pair must
    not contain the BAL token.

    Inputs:
      gov              [Account]:  Governor role account deploys the
                                   OverlayV1BalancerV2Feed contract
      weth             [Contract]: WETH token contract instance
      dai              [Contract]: DAI token contract instance
      balv2_tokens     [tuple]:    BalancerV2Tokens struct field variables
      balweth_poolid [bytes32]:  DAI/WETH Balancer V2 pool id
      pool_daiweth     [Contract]: PAR/USDC Balancer V2 WeightedPool2Tokens
                                   contract instance representing the market
                                   token pair
      pool_balweth    [Contract]:  BAL/WETH Balancer V2 WeightedPool2Tokens
                                   contract instance representing the OVL/WETH
                                   token pair
    '''
    market_pool = pool_daiweth
    ovlweth_pool = pool_balweth
    ovl = dai
    market_base_token = dai
    market_quote_token = weth
    market_base_amount = 1000000
    micro_window = 600
    macro_window = 3600

    with reverts("OVLV1Feed: ovlWethToken != OVL"):
        gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool, ovl,
                   market_base_token, market_quote_token,
                   market_base_amount, balv2_tokens, micro_window,
                   macro_window)
