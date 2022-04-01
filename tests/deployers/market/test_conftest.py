def test_deployer_fixture(deployer, factory, ovl):
    assert deployer.factory() == factory
    assert deployer.ovl() == ovl
