from brownie import web3
from decimal import Decimal
from hexbytes import HexBytes


def calculate_position_info(oi: Decimal,
                            leverage: Decimal,
                            trading_fee_rate: Decimal) -> (Decimal, Decimal,
                                                           Decimal, Decimal):
    """
    Returns position attributes in decimal format (int / 1e18)
    """
    collateral = oi / leverage
    trade_fee = oi * trading_fee_rate
    debt = oi - collateral
    return collateral, oi, debt, trade_fee


def get_position_key(owner: str, id: int) -> HexBytes:
    """
    Returns the position key to retrieve an individual position
    from positions mapping
    """
    return web3.solidityKeccak(['address', 'uint256'], [owner, id])
