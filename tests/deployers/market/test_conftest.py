def test_deployer_fixture(deployer, factory, ov):
    tok, feed, fact = deployer.parameters()
    assert tok == ov
    assert feed == "0x0000000000000000000000000000000000000000"
    assert fact == factory
