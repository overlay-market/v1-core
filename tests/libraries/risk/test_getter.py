from brownie import reverts


def test_get(risk):
    # NOTE: risk.set() tests in test_setter.py
    value = 100
    risk.set(0, 100)

    # check get returns set value
    expect = value
    actual = risk.get(0)
    assert expect == actual


def test_get_reverts_when_non_valid_enum(risk):
    with reverts():
        risk.get(15)
