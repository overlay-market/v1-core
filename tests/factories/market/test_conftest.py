def test_factory_fixture(factory, feed_factory, ovl, gov):
    # check params set properly
    assert factory.ovl() == ovl

    # check appropriate factory roles given to contract deployer
    assert factory.hasRole(factory.ADMIN_ROLE(), gov) is True
    assert factory.hasRole(factory.GOVERNOR_ROLE(), gov) is True

    # check factory has been given admin role on ovl token
    assert ovl.hasRole(ovl.ADMIN_ROLE(), factory) is True

    # check feed factory has been added to registry
    assert factory.isFeedFactory(feed_factory) is True


def test_feed_factory_fixture(feed_factory):
    # check params set properly
    feed_factory.microWindow() == 600
    feed_factory.macroWindow() == 3600
