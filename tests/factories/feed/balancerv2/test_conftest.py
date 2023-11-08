def test_factory_fixture(factory, weth, bal, pool_balweth):
    '''
    Tests that the OverlayV1BalancerV2Factory contract sets the expected
    variables correctly.

    Inputs:
      factory        [Contract]: OverlayV1BalancerV2Factory contract instance
      weth           [Contract]: WETH token contract instance
      dai            [Contract]: DAI token contract instance
      pool_balweth   [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                                 contract instance representing the OVL/WETH
                                 token pair
    '''
    assert factory.ovlWethPool() == pool_balweth
    assert factory.ovl() == bal  # BAL acts as ovl for testing
    assert factory.microWindow() == 600
    assert factory.macroWindow() == 3600
