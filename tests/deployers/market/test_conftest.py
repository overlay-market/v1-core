def test_deployer_fixture(deployer, factory, ovl):
    assert deployer.factory() == factory
    assert deployer.ovl() == ovl

    tok, feed, fact = deployer.parameters()
    assert tok == "0x0000000000000000000000000000000000000000"
    assert feed == "0x0000000000000000000000000000000000000000"
    assert fact == "0x0000000000000000000000000000000000000000"
