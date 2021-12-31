def test_factory_fixture(factory, pool_uniweth_30bps, weth, uni, alice):
    assert factory.ovlWethPool() == pool_uniweth_30bps
    assert factory.ovl() == uni  # UNI acts as ovl for testing
    assert factory.microWindow() == 600
    assert factory.macroWindow() == 3600
