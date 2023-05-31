from brownie import web3
from decimal import Decimal
from hexbytes import HexBytes
from math import log


def get_position_key(owner: str, id: int) -> HexBytes:
    """
    Returns the position key to retrieve an individual position
    from positions mapping
    """
    return web3.solidityKeccak(['address', 'uint256'], [owner, id])


def tick_to_price(tick: int) -> int:
    """
    Returns the price associated with a given tick
    price = 1.0001 ** tick
    """
    return int((Decimal(1.0001) ** Decimal(tick)) * Decimal(1e18))


def price_to_tick(price: int) -> int:
    """
    Returns the tick associated with a given price
    price = 1.0001 ** tick
    """
    return int(log(Decimal(price) / Decimal(1e18)) / log(Decimal(1.0001)))
