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

    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8

    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    pos = (notional, debt, is_long, liquidated, entry_price, oi)
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
    is_long = True
    liquidated = False
    entry_price = 100000000000000000000  # 100
    notional = 10000000000000000000  # 10
    debt = 8000000000000000000  # 8
    oi = (notional / entry_price) * 1000000000000000000  # 0.1

    pos = (notional, debt, is_long, liquidated, entry_price, oi)
    position.set(owner, id, pos)

    # check retrieved position is expected
    expect = pos
    actual = position.get(bob, id)
    assert expect == actual
