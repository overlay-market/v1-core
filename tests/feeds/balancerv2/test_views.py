import pytest
from brownie import Contract, reverts

def test_get_pool_tokens(feed, balv2_tokens):
    '''
    Tests that the OverlayV1BalancerV2Feed contract getPoolTokensData function
    returns the expected token pair when given the associated pool id. 
    Two pool ids are tested:
      1. The OVL/WETH pool id which is often simulated by BAL/WETH for testing
      2. The DAI/WETH pool id which often represents the market token pair for
         testing

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
    '''
    bal_address = '0xba100000625a3754423978a60c9317c58a424e3D'
    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    ovl_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F'  # DAI

    tx_ovl = feed.getPoolTokensData(balv2_tokens[1])
    assert (tx_ovl[0][0] == bal_address)
    assert (tx_ovl[0][1] == weth_address)

    tx_bal = feed.getPoolTokensData(balv2_tokens[2])
    assert (tx_bal[0][0] == ovl_address)
    assert (tx_bal[0][1] == weth_address)

