from brownie import reverts


def test_set(risk):
    values = [idx * 2 + 1 for idx in range(15)]
    for idx in range(15):
        name = risk.getEnumFromUint(idx)
        value = values[idx]
        risk.set(name, value)

        expect = value
        actual = risk.params(idx)
        assert expect == actual


def test_set_reverts_when_non_valid_enum(risk):
    # check reverts if > last enum value
    with reverts():
        risk.set(15, 1)

    # check passes if == last enum value
    risk.set(14, 1)
    expect = 1
    actual = risk.params(14)
    assert expect == actual
