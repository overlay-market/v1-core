def test_to_uint32_bounded(cast):
    value = 1000
    expect = value
    actual = cast.toUint32Bounded(value)
    assert expect == actual


def test_to_uint32_bounded_when_greater_than_max(cast):
    value = 2**165 - 1
    expect = 2**32 - 1
    actual = cast.toUint32Bounded(value)
    assert expect == actual


def test_to_int192_bounded(cast):
    # check for positive values
    value = 1000
    expect = value
    actual = cast.toInt192Bounded(value)
    assert expect == actual

    # check for negative values
    value = -1000
    expect = value
    actual = cast.toInt192Bounded(value)
    assert expect == actual


def test_to_int192_bounded_when_less_than_min(cast):
    value = -2**250
    expect = -2**191
    actual = cast.toInt192Bounded(value)
    assert expect == actual


def test_to_int192_bounded_when_greater_than_max(cast):
    value = 2**250 - 1
    expect = 2**191 - 1
    actual = cast.toInt192Bounded(value)
    assert expect == actual
