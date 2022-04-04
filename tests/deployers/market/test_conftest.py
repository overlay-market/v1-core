def test_deployer_fixture(deployer, factory, ovl):
    assert deployer.factory() == factory
    assert deployer.ovl() == ovl

    tok, feed, fact = deployer.parameters()
    assert tok == ovl
    assert feed == "0x0000000000000000000000000000000000000000"
    assert fact == factory
