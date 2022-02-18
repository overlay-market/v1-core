from pytest import approx


def test_pow_up(fixed_point):
    # test for x**2 and x**(1/2)
    x = 500000000000000000  # 0.5

    # check pow returns 1/4 when base is 1/2 and exponent is 2
    y = 2000000000000000000  # 2
    expect = 250000000000000000  # 0.25
    actual = fixed_point.powUp(x, y)
    assert expect == approx(actual)

    # check pow returns 1/sqrt(2) when base is 1/2 and exponent is 1/2
    y = 500000000000000000  # 0.5
    expect = 707106781186547456  # 0.707106781186547456
    actual = fixed_point.powUp(x, y)
    assert expect == approx(actual)


def test_pow_up_when_base_is_zero_and_power_is_nonzero(fixed_point):
    x = 0  # base is zero
    y = int(10 * 1e18)  # power is nonzero

    # check pow returns 0 when base is zero and exponent is nonzero
    expect = 0
    actual = fixed_point.powUp(x, y)
    assert expect == actual


def test_pow_up_when_base_is_zero_and_power_is_zero(fixed_point):
    x = 0  # base is zero
    y = 0  # power is zero

    # check pow returns 1 when base is zero and exponent
    # is zero: 0^0 resolves to 1
    expect = int(1e18)
    actual = fixed_point.powUp(x, y)
    assert expect == actual


def test_pow_up_when_base_is_one_and_power_is_nonzero(fixed_point):
    x = int(1e18)  # base is ONE
    y = int(10 * 1e18)  # power is nonzero

    # check pow returns 1 when base is one and exponent is nonzero
    expect = int(1e18)
    actual = fixed_point.powUp(x, y)
    assert expect == actual


def test_pow_up_when_base_is_one_and_power_is_zero(fixed_point):
    x = int(1e18)  # base is ONE
    y = 0  # power is zero

    # check pow returns 1 when base is one and exponent is zero
    expect = int(1e18)
    actual = fixed_point.powUp(x, y)
    assert expect == actual


def test_pow_down(fixed_point):
    # test for x**2 and x**(1/2)
    x = 500000000000000000  # 0.5

    # check pow returns 1/4 when base is 1/2 and exponent is 2
    y = 2000000000000000000  # 2
    expect = 250000000000000000  # 0.25
    actual = fixed_point.powDown(x, y)

    assert expect == approx(actual)

    # check pow returns 1/sqrt(2) when base is 1/2 and exponent is 1/2
    y = 500000000000000000  # 0.5
    expect = 707106781186547456  # 0.707106781186547456
    actual = fixed_point.powDown(x, y)
    assert expect == approx(actual)


def test_pow_down_when_base_is_zero_and_power_is_nonzero(fixed_point):
    x = 0  # base is zero
    y = int(10 * 1e18)  # power is nonzero

    # check pow returns 0 when base is zero and exponent is nonzero
    expect = 0
    actual = fixed_point.powDown(x, y)
    assert expect == actual


def test_pow_down_when_base_is_zero_and_power_is_zero(fixed_point):
    x = 0  # base is zero
    y = 0  # power is zero

    # check pow returns 1 when base is zero and exponent
    # is zero: 0^0 resolves to 1
    expect = int(1e18)
    actual = fixed_point.powDown(x, y)
    assert expect == actual


def test_pow_down_when_base_is_one_and_power_is_nonzero(fixed_point):
    x = int(1e18)  # base is ONE
    y = int(10 * 1e18)  # power is zero

    # check pow returns 1 when base is one and exponent is nonzero
    expect = int(1e18)
    actual = fixed_point.powDown(x, y)
    assert expect == actual


def test_pow_down_when_base_is_one_and_power_is_zero(fixed_point):
    x = int(1e18)  # base is ONE
    y = 0  # power is zero

    # check pow returns 1 when base is one and exponent is zero
    expect = int(1e18)
    actual = fixed_point.powDown(x, y)
    assert expect == actual
