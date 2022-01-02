def test_factory_fixture(factory, ovl, gov):
    # check params set properly
    assert factory.ovl() == ovl

    # check appropriate factory roles given to contract deployer
    assert factory.hasRole(factory.ADMIN_ROLE(), gov) is True
    assert factory.hasRole(factory.GOVERNOR_ROLE(), gov) is True

    # check factory has been given admin role on ovl token
    assert ovl.hasRole(ovl.ADMIN_ROLE(), factory) is True
