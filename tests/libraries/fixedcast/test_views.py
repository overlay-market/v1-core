from brownie import reverts
from brownie.test import given, strategy
from decimal import Decimal


@given(value=strategy('uint16'))
def test_to_uint256_fixed(fixed_cast, value):
    # convert 4 places to 18 places
    expect = int(Decimal(1e14) * Decimal(value))
    actual = fixed_cast.toUint256Fixed(value)
    assert expect == actual


@given(value=strategy('decimal', min_value="0.000001", max_value="6.5535",
                      places=6))
def test_to_uint16_fixed(fixed_cast, value):
    # convert 18 places to 4 places
    value = value * Decimal(1e18)
    expect = int(Decimal(value) / Decimal(1e14))
    actual = fixed_cast.toUint16Fixed(value)
    assert expect == actual


@given(value=strategy('decimal', min_value="0.000001", max_value="6.5535",
                      places=6))
def test_to_uint16_to_uint256_fixed(fixed_cast, value):
    # convert 18 places to 4 places back to 18 places rounded down
    value = value * Decimal(1e18)
    expect = int(Decimal(int(Decimal(value) / Decimal(1e14))) * Decimal(1e14))
    actual = fixed_cast.toUint256Fixed(fixed_cast.toUint16Fixed(value))
    assert expect == actual


def test_to_uint16_fixed_reverts_when_gt_max(fixed_cast):
    # should pass for type(uint16).max
    value = 2**16 - 1
    input_value = value * Decimal(1e14)
    expect = value
    actual = fixed_cast.toUint16Fixed(input_value)
    assert expect == actual

    # should fail for type(uint16).max + 1
    value = 2**16
    input_value = value * Decimal(1e14)
    with reverts("OVLV1: FixedCast out of bounds"):
        fixed_cast.toUint16Fixed(input_value)
