import pytest
from brownie import reverts
from brownie.test import given, strategy
from decimal import Decimal

from .utils import calculate_position_info, get_position_key


# NOTE: Tests passing with isolation fixture
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@given(is_long=strategy('bool'))
def test_build_when_price_limit_is_breached(market, feed, alice, ovl, is_long):
    # get position key/id related info
    expect_pos_id = market.nextPositionId()

    # build attributes
    # TODO: oi => notional
    oi = Decimal(100)
    leverage = Decimal(1.5)

    # tolerance
    tol = 1e-3

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # calculate expected entry price
    # NOTE: ask(), bid() tested in test_price.py
    # NOTE: capNotional(), capOi() tested in test_oi_cap.py
    data = feed.latest()
    cap_notional = Decimal(market.capNotionalAdjustedForBounds(
        data, market.capNotional())) / Decimal(1e18)
    volume = int((oi / cap_notional) * Decimal(1e18))
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
    market.build(input_collateral, input_leverage, input_is_long,
                 input_price_limit, {"from": alice})

    # check position created through id increment
    expect_pos_id += 1
    actual = market.nextPositionId()
    assert expect_pos_id == actual


@given(is_long=strategy('bool'))
def test_unwind_when_price_limit_is_breached(market, feed, alice, factory, ovl,
                                             is_long):
    # build attributes
    notional = Decimal(100)
    leverage = Decimal(1.5)

    # tolerance
    tol = 1e-3

    # so don't have to worry about funding
    market.setK(0, {"from": factory})

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    (actual_notional, _, _, _, actual_entry_price, _) = pos
    oi = Decimal(actual_notional) / Decimal(actual_entry_price)

    # calculate expected exit price
    # NOTE: ask(), bid() tested in test_price.py
    # NOTE: capNotional(), capOi() tested in test_oi_cap.py
    data = feed.latest()
    cap_notional = Decimal(market.capNotionalAdjustedForBounds(
        data, market.capNotional())) / Decimal(1e18)
    cap_oi = Decimal(market.capOi(data, cap_notional))
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
    expect_notional = 0
    expect_debt = 0

    actual_pos = market.positions(expect_pos_key)
    (actual_notional, actual_debt, _, _, _, _) = actual_pos

    assert expect_notional == actual_notional
    assert expect_debt == actual_debt
