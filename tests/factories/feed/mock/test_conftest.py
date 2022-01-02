def test_factory_fixture(factory):
    assert factory.microWindow() == 600
    assert factory.macroWindow() == 3600
