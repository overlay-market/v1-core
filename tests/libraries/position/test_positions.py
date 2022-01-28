from brownie import web3
from hexbytes import HexBytes


def get_position_key(owner: str, id: int) -> HexBytes:
    """
    Returns the position key to retrieve an individual position
    from positions mapping
    """
    return web3.solidityKeccak(['address', 'uint256'], [owner, id])


def test_positions_setter(position, alice):
    owner = alice
    id = 0

    oi = 10000000000000000000  # 10
    cost = 2000000000000000000  # 2
    debt = 8000000000000000000  # 8
    entry_price = 100000000000000000000  # 100
    is_long = True

    pos = (is_long, oi, cost, debt, entry_price)
    position.set(owner, id, pos)

    # pos key
    pos_key = get_position_key(alice.address, id)

    # check position was added to positions mapping
    expect = pos
    actual = position.positions(pos_key)
    assert expect == actual


def test_positions_getter(position, bob):
    owner = bob
    id = 1

    # add the position first
    oi = 10000000000000000000  # 10
    cost = 2000000000000000000  # 2
    debt = 8000000000000000000  # 8
    entry_price = 100000000000000000000  # 100
    is_long = True

    pos = (is_long, oi, cost, debt, entry_price)
    position.set(owner, id, pos)

    # check retrieved position is expected
    expect = pos
    actual = position.get(bob, id)
    assert expect == actual
