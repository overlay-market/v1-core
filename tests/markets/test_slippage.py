import pytest
from brownie import reverts
from brownie.test import given, strategy
from decimal import Decimal

from .utils import (
    calculate_position_info, get_position_key, mid_from_feed, RiskParameter
)


# NOTE: Tests passing with isolation fixture
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@given(is_long=strategy('bool'))
def test_build_when_price_limit_is_breached(market, feed, alice, ovl, is_long):
    # NOTE: current position id is zero given isolation fixture
    expect_pos_id = 0

    # build attributes
    notional = Decimal(100)
    leverage = Decimal(1.5)

    # tolerance
    tol = 3e-4

    # calculate expected pos info data
    trading_fee_rate = Decimal(
        market.params(RiskParameter.TRADING_FEE_RATE.value) / 1e18)
    collateral, notional, debt, trade_fee \
        = calculate_position_info(notional, leverage, trading_fee_rate)

    # calculate expected entry price
    # NOTE: ask(), bid() tested in test_price.py
    # NOTE: capNotional(), oiFromNotional() tested in test_oi_cap.py
    data = feed.latest()
    mid = mid_from_feed(data)

    oi = market.oiFromNotional(int(notional * Decimal(1e18)), mid)
    cap_notional = Decimal(market.capNotionalAdjustedForBounds(
        data, market.params(RiskParameter.CAP_NOTIONAL.value)))
    cap_oi = Decimal(market.oiFromNotional(cap_notional, mid))
    volume = int((oi / cap_oi) * Decimal(1e18))

    price = market.ask(data, volume) if is_long else market.bid(data, volume)

    # input values for tx
    input_collateral = int((collateral) * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})

    # check build reverts when price surpasses limit
    input_price_limit = price * (1 - tol) if is_long else price * (1 + tol)
    with reverts("OVLV1:slippage>max"):
        market.build(input_collateral, input_leverage, input_is_long,
                     input_price_limit, {"from": alice})

    # check build succeeds when price does not surpass limit
    input_price_limit = price * (1 + tol) if is_long else price * (1 - tol)
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})

    # check position created through id increment
    actual_pos_id = tx.return_value
    assert expect_pos_id == actual_pos_id


@given(is_long=strategy('bool'))
def test_unwind_when_price_limit_is_breached(market, feed, alice, factory, ovl,
                                             is_long):
    # build attributes
    notional = Decimal(100)
    leverage = Decimal(1.5)

    # tolerance
    tol = 3e-4

    # so don't have to worry about funding
    market.setRiskParam(RiskParameter.K.value, 0, {"from": factory})

    # calculate expected pos info data
    trading_fee_rate = Decimal(
        market.params(RiskParameter.TRADING_FEE_RATE.value) / 1e18)
    collateral, notional, debt, trade_fee \
        = calculate_position_info(notional, leverage, trading_fee_rate)

    # input values for tx
    input_collateral = int((collateral) * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long
    input_price_limit = 2**256-1 if is_long else 0

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    pos = market.positions(pos_key)
    (actual_notional, _, _, _, _, _, _, actual_fraction) = pos

    # calculate expected exit price
    # NOTE: ask(), bid() tested in test_price.py
    # NOTE: capNotional(), oiFromNotional() tested in test_oi_cap.py
    data = feed.latest()
    mid = mid_from_feed(data)

    oi = market.oiFromNotional(actual_notional, mid)
    cap_notional = Decimal(market.capNotionalAdjustedForBounds(
        data, market.params(RiskParameter.CAP_NOTIONAL.value)))
    cap_oi = Decimal(market.oiFromNotional(cap_notional, mid))
    volume = int((oi / cap_oi) * Decimal(1e18))

    price = market.bid(data, volume) if is_long else market.ask(data, volume)

    # input values
    input_pos_id = pos_id
    input_fraction = 1e18

    # check unwind reverts when price surpasses limit
    input_price_limit = price * (1 + tol) if is_long else price * (1 - tol)
    with reverts("OVLV1:slippage>max"):
        market.unwind(input_pos_id, input_fraction, input_price_limit,
                      {"from": alice})

    # check unwind succeeds when price does not surpass limit
    input_price_limit = price * (1 - tol) if is_long else price * (1 + tol)
    market.unwind(input_pos_id, input_fraction, input_price_limit,
                  {"from": alice})

    # check all oi shares removed
    expect_pos_key = get_position_key(alice.address, input_pos_id)
    expect_oi_shares = 0
    expect_fraction = 0

    actual_pos = market.positions(expect_pos_key)
    (_, _, _, _, _, _, actual_oi_shares, actual_fraction) = actual_pos
    assert expect_fraction == actual_fraction
    assert expect_oi_shares == actual_oi_shares
