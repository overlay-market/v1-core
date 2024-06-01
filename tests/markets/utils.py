from brownie import web3
from decimal import Decimal
from enum import Enum
from hexbytes import HexBytes
from math import log, exp, sqrt
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


def oi_after_funding(time_delta: int,
                     oi_long: Decimal,
                     oi_short: Decimal,
                     k: Decimal) -> (Decimal, Decimal):
    """
    Return the long oi and short oi for market after applying funding rates
    """
    if time_delta <= 0:
        return (oi_long, oi_short)
    is_long_overweighted = oi_long > oi_short
    (oi_overweight, oi_underweight) = (
        oi_long, oi_short) if is_long_overweighted else (oi_short, oi_long)
    oi_total = oi_overweight + oi_underweight
    oi_imbalance = oi_overweight - oi_underweight
    oi_invariant = oi_underweight * oi_overweight

    if oi_imbalance == 0 or oi_total == 0:
        return (oi_long, oi_short)

    expect_oi = oi_total * Decimal(
        sqrt(1 - (oi_imbalance/oi_total)**2 * Decimal(
            1 - exp(-4*k*time_delta))))
    expect_oi_imb = oi_imbalance * Decimal(exp(-2*k*time_delta))

    expect_oi_overweight = (expect_oi + expect_oi_imb) / 2
    expect_oi_underweight = oi_invariant / expect_oi_overweight

    return (expect_oi_overweight,
            expect_oi_underweight) if is_long_overweighted else (
                expect_oi_underweight, expect_oi_overweight)
