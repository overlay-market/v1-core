from brownie import web3
from decimal import Decimal
from enum import Enum
from hexbytes import HexBytes
from typing import Any


class RiskParameter(Enum):
    K = 0
    LMBDA = 1
    DELTA = 2
    CAP_PAYOFF = 3
    CAP_NOTIONAL = 4
    CAP_LEVERAGE = 5
    CIRCUIT_BREAKER_WINDOW = 6
    CIRCUIT_BREAKER_MINT_TARGET = 7
    MAINTENANCE_MARGIN_FRACTION = 8
    MAINTENANCE_MARGIN_BURN_RATE = 9
    LIQUIDATION_FEE_RATE = 10
    TRADING_FEE_RATE = 11
    MIN_COLLATERAL = 12
    PRICE_DRIFT_UPPER_LIMIT = 13
    AVERAGE_BLOCK_TIME = 14


def calculate_position_info(notional: Decimal,
                            leverage: Decimal,
                            trading_fee_rate: Decimal) -> (Decimal, Decimal,
                                                           Decimal, Decimal):
    """
    Returns position attributes in decimal format (int / 1e18)
    """
    collateral = notional / leverage
    trade_fee = notional * trading_fee_rate
    debt = notional - collateral
    return collateral, notional, debt, trade_fee


def get_position_key(owner: str, id: int) -> HexBytes:
    """
    Returns the position key to retrieve an individual position
    from positions mapping
    """
    return web3.solidityKeccak(['address', 'uint256'], [owner, id])


def mid_from_feed(data: Any) -> float:
    """
    Returns mid price from oracle feed data
    """
    (_, _, _, price_micro, price_macro, _, _, _) = data
    ask = max(price_micro, price_macro)
    bid = min(price_micro, price_macro)
    mid = (ask + bid) / 2
    return mid


def entry_from_mid_ratio(mid_ratio: int, mid: int) -> int:
    """
    Returns entry price from mid ratio and mid price

    NOTE: mid_ratio is uint48 format and mid price is int FixedPoint format
    """
    # NOTE: mid_ratio "ONE" is 1e14 given uint48
    entry_price = int((Decimal(mid_ratio) / Decimal(1e14)) * mid)
    return entry_price


def calculate_mid_ratio(entry_price: int, mid_price: int) -> int:
    """
    Returns mid ratio from entry price and mid price

    NOTE: mid_ratio is uint48 format and mid, entry prices
    are int FixedPoint format
    """
    # NOTE: mid_ratio "ONE" is 1e14 given uint48
    mid_ratio = int(Decimal(entry_price) * Decimal(1e14) / Decimal(mid_price))
    return mid_ratio


def oi_from_oi_ratio(oi_ratio: int, oi_shares: int) -> int:
    """
    Returns oi associated with position from oi_ratio and oi_shares
    """
    # NOTE: oi_ratio "ONE" is 1e18 given uint256
    oi = int(Decimal(oi_shares) * Decimal(oi_ratio) / Decimal(1e18))
    return oi


def calculate_oi_ratio(oi: int, oi_shares: int) -> int:
    """
    Returns oi ratio from oi and oi_shares
    """
    # NOTE: "ONE" is 1e18 given uint256
    oi_ratio = int(Decimal(oi) * Decimal(1e18)) / Decimal(oi_shares)
    return oi_ratio
