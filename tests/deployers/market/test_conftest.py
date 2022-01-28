def test_deployer_fixture(deployer, factory):
    assert deployer.factory() == factory
