import pytest
from pytest import approx
from brownie import chain
from brownie.test import given, strategy
from decimal import Decimal
from math import exp

from .utils import calculate_position_info, get_position_key


# NOTE: Tests passing with isolation fixture
# TODO: Fix tests to pass even without isolation fixture (?)
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@given(is_long=strategy('bool'))
def test_liquidate_updates_position(mock_market, mock_feed, alice, rando,
                                    ovl, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    trading_fee_rate = Decimal(mock_market.tradingFeeRate() / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(oi_initial, leverage, trading_fee_rate)

    # input values for build
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 2**256-1 if is_long else 0

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(mock_market, approve_collateral, {"from": alice})
    tx = mock_market.build(input_collateral, input_leverage, input_is_long,
                           input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = mock_market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    tx = mock_market.update({"from": rando})
    _ = tx.return_value

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_cost = Decimal(expect_oi_shares - expect_debt)
    liq_debt = Decimal(expect_debt)
    liq_collateral = liq_oi - liq_debt

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    maintenance_fraction = Decimal(mock_market.maintenanceMarginFraction()) \
        / Decimal(1e18)
    delta = Decimal(mock_market.delta()) / Decimal(1e18)
    if is_long:
        expect_liquidation_price = Decimal(expect_entry_price) * \
            (maintenance_fraction * Decimal(expect_oi_shares)
             + Decimal(expect_debt)) / expect_oi_current
    else:
        expect_liquidation_price = expect_entry_price * \
            (2 - (maintenance_fraction * Decimal(expect_oi_shares)
             + Decimal(expect_debt)) / expect_oi_current)

    # change price by factor so position becomes liquidatable
    # NOTE: Is simply liq_price but adjusted for prior to static spread applied
    # NOTE: price_multiplier = (liq_price / entry_price) / (1 + spread); ask
    # NOTE:                  = (liq_price / entry_price) * (1 + spread); bid
    price_multiplier = expect_liquidation_price / Decimal(expect_entry_price)
    if is_long:
        # longs get the bid on exit, which has e**(-delta) multiplied to it
        # mock feed price should then be liq price * e**(delta) to account
        price_multiplier *= Decimal(exp(delta)) / Decimal(1 + tol)
    else:
        # shorts get the ask on exit, which has e**(+delta) multiplied to it
        # mock feed price should then be liq price * e**(-delta) to account
        price_multiplier *= Decimal(exp(-delta)) * Decimal(1 + tol)

    price = Decimal(mock_feed.price()) * price_multiplier
    mock_feed.setPrice(price)

    # calculate expected exit price
    # NOTE: no volume should be added to rollers on liquidate
    data = mock_feed.latest()
    expect_exit_price = mock_market.bid(data, 0) if is_long \
        else mock_market.ask(data, 0)

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # adjust oi shares, debt position attributes to zero
    # liquidated flips to true
    expect_oi_shares = 0
    expect_debt = 0
    expect_liquidated = True

    # check expected pos attributes match actual after liquidate
    (actual_oi_shares, actual_debt, actual_is_long, actual_liquidated,
     actual_entry_price) = mock_market.positions(pos_key)

    assert actual_oi_shares == expect_oi_shares
    assert actual_debt == expect_debt
    assert actual_is_long == expect_is_long
    assert actual_liquidated == expect_liquidated
    assert actual_entry_price == expect_entry_price

    # check liquidate event with expected values
    assert "Liquidate" in tx.events
    assert tx.events["Liquidate"]["sender"] == rando.address
    assert tx.events["Liquidate"]["owner"] == alice.address
    assert tx.events["Liquidate"]["positionId"] == pos_id

    # check expected liquidate price matches actual
    actual_exit_price = int(tx.events["Liquidate"]["price"])
    assert actual_exit_price == approx(expect_exit_price, rel=1e-4)

    # calculate expected values for burn comparison
    if is_long:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(actual_exit_price) / Decimal(expect_entry_price) - 1)
    else:
        liq_pnl = Decimal(expect_oi_current) * \
            (1 - Decimal(actual_exit_price) / Decimal(expect_entry_price))

    expect_value = int(liq_collateral + liq_pnl)
    expect_cost = int(liq_cost)

    # adjust value for maintenance burn
    maintenance_burn = Decimal(mock_market.maintenanceMarginBurnRate()) \
        / Decimal(1e18)
    expect_value -= int(expect_value * maintenance_burn)
    expect_mint = expect_value - expect_cost

    actual_mint = int(tx.events["Liquidate"]["mint"])
    assert actual_mint == approx(expect_mint, rel=1e-4)
