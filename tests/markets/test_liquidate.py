import pytest
from pytest import approx
from brownie import chain, reverts
from brownie.test import given, strategy
from decimal import Decimal

from .utils import (
    calculate_position_info,
    get_position_key,
    mid_from_feed,
    tick_to_price,
    RiskParameter
)


# NOTE: Tests passing with isolation fixture
# TODO: Fix tests to pass even without isolation fixture (?)
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@given(is_long=strategy('bool'))
def test_liquidate_updates_position(mock_market, mock_feed, alice, rando,
                                    ovl, is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_cost = Decimal(expect_notional - expect_debt)
    liq_debt = Decimal(expect_debt)
    liq_collateral = liq_notional * (liq_oi / liq_oi_initial) - liq_debt

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # calculate expected exit price
    # NOTE: no volume should be added to rollers on liquidate
    # NOTE: use the mid price
    data = mock_feed.latest()
    expect_liq_price = int(mid_from_feed(data))

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # cache entry price at build for mint calcs later
    entry_price = expect_entry_price

    # liquidated flips to true and sets fractionRemaining to zero
    expect_liquidated = True
    expect_oi_shares = 0
    expect_fraction_remaining = 0

    # check expected pos attributes match actual after liquidate
    (actual_notional, actual_debt, actual_mid_tick, actual_entry_tick,
     actual_is_long, actual_liquidated, actual_oi_shares,
     actual_fraction_remaining) = mock_market.positions(pos_key)

    assert actual_notional == expect_notional
    assert actual_debt == expect_debt
    assert actual_mid_tick == expect_mid_tick
    assert actual_entry_tick == expect_entry_tick
    assert actual_is_long == expect_is_long
    assert actual_liquidated == expect_liquidated
    assert actual_oi_shares == expect_oi_shares
    assert actual_fraction_remaining == expect_fraction_remaining

    # check liquidate event with expected values
    assert "Liquidate" in tx.events
    assert tx.events["Liquidate"]["sender"] == rando.address
    assert tx.events["Liquidate"]["owner"] == alice.address
    assert tx.events["Liquidate"]["positionId"] == pos_id

    # check expected liquidate price matches actual
    actual_liq_price = int(tx.events["Liquidate"]["price"])
    assert actual_liq_price == approx(expect_liq_price)

    # calculate expected values for burn comparison
    if is_long:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(actual_liq_price) - Decimal(entry_price)) \
            / Decimal(1e18)
    else:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(entry_price) - Decimal(actual_liq_price)) \
            / Decimal(1e18)

    expect_value = int(liq_collateral + liq_pnl)
    expect_cost = int(liq_cost)

    # adjust value for maintenance burn
    idx_mmbr = RiskParameter.MAINTENANCE_MARGIN_BURN_RATE.value
    maintenance_burn = Decimal(mock_market.params(idx_mmbr)) \
        / Decimal(1e18)

    # remove liquiation fee from remaining margin
    liq_fee = int(expect_value * liq_fee_rate)
    margin_remaining = expect_value - liq_fee

    expect_value -= int(margin_remaining * maintenance_burn)
    expect_mint = expect_value - expect_cost
    actual_mint = int(tx.events["Liquidate"]["mint"])

    assert actual_mint == approx(expect_mint)


@given(is_long=strategy('bool'))
def test_liquidate_removes_oi(mock_market, mock_feed, alice, rando, ovl,
                              is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_oi_shares = Decimal(expect_oi_shares)
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1 - liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1 - liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    _ = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # get actual oi values after liquidate
    actual_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    actual_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()

    # calculate actual liquidated oi shares from aggregate changes
    actual_liq_oi_shares = expect_total_oi_shares - actual_total_oi_shares

    # calculate actual liq oi shares from position
    (_, _, _, _, _, _, actual_oi_shares,
     actual_fraction_remaining) = mock_market.positions(pos_key)
    actual_liq_pos_oi_shares = expect_oi_shares - actual_oi_shares

    # adjust total oi and total oi shares downward for liquidate
    expect_total_oi -= int(liq_oi)
    expect_total_oi_shares -= int(liq_oi_shares)

    # check actual oi aggregates matches expected
    assert int(actual_total_oi) == approx(expect_total_oi)
    assert actual_total_oi_shares == expect_total_oi_shares

    # check actual liq aggregate oi shares matches pos oi shares liquidated
    assert actual_liq_oi_shares == actual_liq_pos_oi_shares


def test_liquidate_updates_market(mock_market, mock_feed, alice, rando, ovl):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # cache prior timestamp update last value
    prior_timestamp_update_last = mock_market.timestampUpdateLast()

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    mock_feed.setPrice(liq_price, {"from": rando})

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # get the expected timestamp and check equal to actual
    expect_timestamp_update_last = chain[tx.block_number]['timestamp']
    actual_timestamp_update_last = mock_market.timestampUpdateLast()

    assert actual_timestamp_update_last == expect_timestamp_update_last
    assert actual_timestamp_update_last != prior_timestamp_update_last


@given(is_long=strategy('bool'))
def test_liquidate_registers_zero_volume(mock_market, mock_feed, alice, rando,
                                         ovl, is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # priors actual values. longs get the bid, shorts get the ask on liquidate
    snapshot_volume = mock_market.snapshotVolumeBid() if is_long \
        else mock_market.snapshotVolumeAsk()
    last_timestamp, last_window, last_volume = snapshot_volume

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # get the micro window
    data = mock_feed.latest()
    _, micro_window, _, _, _, _, _, _ = data

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # calculate expect values for snapshot
    # NOTE: should be zeros across the board since no positions built on opp
    # side to initial build
    expect_timestamp = 0
    expect_window = 0
    expect_volume = last_volume

    # check expect == actual for snapshot volume
    actual = mock_market.snapshotVolumeBid() if is_long else \
        mock_market.snapshotVolumeAsk()
    actual_timestamp, actual_window, actual_volume = actual

    assert actual_timestamp == expect_timestamp
    assert actual_window == expect_window
    assert actual_volume == expect_volume


@given(is_long=strategy('bool'))
def test_liquidate_registers_mint_or_burn(mock_market, mock_feed, alice, rando,
                                          ovl, is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # priors actual values for snapshot of minted roller
    snapshot_minted = mock_market.snapshotMinted()
    last_timestamp, last_window, last_minted = snapshot_minted

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # get the micro window
    data = mock_feed.latest()
    _, micro_window, _, _, _, _, _, _ = data

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})
    actual_mint = tx.events["Liquidate"]["mint"]

    # calculate expected rolling minted and window numbers when
    # adjusted for decay
    # NOTE: decayOverWindow() tested in test_rollers.py
    input_minted = int(actual_mint)
    input_window = int(
        mock_market.params(RiskParameter.CIRCUIT_BREAKER_WINDOW.value))
    input_timestamp = chain[tx.block_number]['timestamp']

    # expect accumulator now to be calculated as
    # accumulatorLast * (1 - dt/windowLast) + value
    dt = input_timestamp - last_timestamp
    last_minted_decayed = last_minted * (1 - dt/last_window) \
        if last_window != 0 and dt >= last_window else 0
    expect_minted = int(last_minted_decayed + input_minted)

    # expect window now to be calculated as weighted average
    # of remaining time left in last window and total time in new window
    # weights are accumulator values for the respective time window
    numerator = int((last_window - dt) * abs(last_minted_decayed)
                    + input_window * abs(input_minted))
    expect_window = int(numerator
                        / (abs(last_minted_decayed) + abs(input_minted)))
    expect_timestamp = input_timestamp

    # check expect == actual for snapshot minted
    actual = mock_market.snapshotMinted()
    actual_timestamp, actual_window, actual_minted = actual

    assert actual_timestamp == expect_timestamp
    assert actual_window == expect_window
    assert actual_minted == expect_minted


@given(is_long=strategy('bool'))
def test_liquidate_executes_transfers(mock_market, mock_feed, alice, rando,
                                      factory, ovl, is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_cost = Decimal(expect_notional - expect_debt)
    liq_debt = Decimal(expect_debt)
    liq_collateral = liq_notional * (liq_oi / liq_oi_initial) - liq_debt

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # get expected exit price
    price = tx.events["Liquidate"]["price"]

    # calculate expected values for burn comparison
    if is_long:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(price) - Decimal(expect_entry_price)) \
            / Decimal(1e18)
    else:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(expect_entry_price) - Decimal(price)) \
            / Decimal(1e18)

    liq_value = int(liq_collateral + liq_pnl)
    liq_cost = int(liq_cost)

    # remove liquiation fee from remaining margin
    liq_fee = int(liq_value * liq_fee_rate)
    margin_remaining = liq_value - liq_fee

    # adjust value for maintenance burn
    idx_mmbr = RiskParameter.MAINTENANCE_MARGIN_BURN_RATE.value
    maintenance_burn = Decimal(mock_market.params(idx_mmbr)) \
        / Decimal(1e18)
    margin_burned = int(margin_remaining * maintenance_burn)
    margin_remaining -= margin_burned

    # calculate expected values
    # expect_value -= int(remaining_margin * maintenance_burn)
    expect_mint = int(liq_value - liq_cost - margin_burned)

    # check expected pnl in line with Liquidate event first
    actual_mint = tx.events["Liquidate"]["mint"]
    assert int(actual_mint) == approx(expect_mint)

    # Examine transfer event to verify burn happened
    expect_mint_from = mock_market.address
    expect_mint_to = "0x0000000000000000000000000000000000000000"
    expect_mint_mag = abs(expect_mint)

    # liquidation fee expected
    expect_liq_fee = int(liq_fee)

    # value less fees expected
    expect_value_out = int(margin_remaining)

    # check Transfer events for:
    # 1. burn pnl; 2. value less liq fees out for reward; 3. liq fees out
    assert 'Transfer' in tx.events
    assert len(tx.events['Transfer']) == 3

    # check actual amount burned is in line with expected (1)
    assert tx.events["Transfer"][0]["from"] == expect_mint_from
    assert tx.events["Transfer"][0]["to"] == expect_mint_to
    assert int(tx.events["Transfer"][0]["value"]) == approx(
        expect_mint_mag, rel=1.05e-6)

    # check liquidate event has same value for burn as transfer event (1)
    actual_transfer_mint = -tx.events["Transfer"][0]["value"]
    assert tx.events["Liquidate"]["mint"] == actual_transfer_mint

    # check liquidation fee paid to liquidator in event (2)
    assert tx.events['Transfer'][1]['from'] == mock_market.address
    assert tx.events['Transfer'][1]['to'] == rando.address
    assert int(tx.events['Transfer'][1]['value']) == approx(
        expect_liq_fee, rel=1.05e-6)

    # check remaining margin sent to fee recipient (3)
    assert tx.events['Transfer'][2]['from'] == mock_market.address
    assert tx.events['Transfer'][2]['to'] == factory.feeRecipient()
    assert int(tx.events['Transfer'][2]['value']) == approx(
        expect_value_out, rel=1.05e-6)


# TODO: check for correctness again
@given(is_long=strategy('bool'))
def test_liquidate_transfers_fee_to_liquidator(mock_market, mock_feed, alice,
                                               rando, ovl, is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_cost = Decimal(expect_notional - expect_debt)
    liq_debt = Decimal(expect_debt)
    liq_collateral = liq_notional * (liq_oi / liq_oi_initial) - liq_debt

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # priors actual values
    expect_balance_rando = ovl.balanceOf(rando)
    expect_balance_market = ovl.balanceOf(mock_market)

    # calculate position attributes at the current time
    # ignore payoff cap
    liq_cost = Decimal(expect_notional - expect_debt)

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # readjust expect market balance for burn
    actual_mint = tx.events["Liquidate"]["mint"]
    expect_balance_market += actual_mint

    # calculate expected values
    expect_cost_plus_mint = int(liq_cost + actual_mint)

    # get expected exit price
    price = tx.events["Liquidate"]["price"]

    # calculate expected values for burn comparison
    if is_long:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(price) - Decimal(expect_entry_price)) \
            / Decimal(1e18)
    else:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(expect_entry_price) - Decimal(price)) \
            / Decimal(1e18)

    liq_value = int(liq_collateral + liq_pnl)
    liq_cost = int(liq_cost)

    # get the liquidation fee
    expect_liq_fee = int(liq_value * liq_fee_rate)

    expect_balance_rando += expect_liq_fee
    expect_balance_market -= expect_cost_plus_mint

    actual_balance_rando = ovl.balanceOf(rando)
    actual_balance_market = ovl.balanceOf(mock_market)

    assert int(actual_balance_rando) == approx(
        expect_balance_rando, rel=1.05e-6)
    assert int(actual_balance_market) == approx(
        expect_balance_market, rel=1.05e-6)


# TODO: check for correctness again
@given(is_long=strategy('bool'))
def test_liquidate_transfers_remaining_margin(mock_market, mock_feed, alice,
                                              factory, rando, ovl, is_long):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_cost = Decimal(expect_notional - expect_debt)
    liq_debt = Decimal(expect_debt)
    liq_collateral = liq_notional * (liq_oi / liq_oi_initial) - liq_debt

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # priors actual values
    recipient = factory.feeRecipient()
    expect_balance_recipient = ovl.balanceOf(recipient)
    expect_balance_market = ovl.balanceOf(mock_market)

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # readjust expect market balance for burn
    actual_mint = tx.events["Liquidate"]["mint"]
    expect_balance_market += actual_mint

    # calculate expected values
    expect_cost_plus_mint = int(liq_cost + actual_mint)

    # get expected exit price
    price = tx.events["Liquidate"]["price"]

    # calculate expected values for burn comparison
    if is_long:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(price) - Decimal(expect_entry_price)) \
            / Decimal(1e18)
    else:
        liq_pnl = Decimal(expect_oi_current) * \
            (Decimal(expect_entry_price) - Decimal(price)) \
            / Decimal(1e18)

    liq_value = int(liq_collateral + liq_pnl)
    liq_cost = int(liq_cost)

    # remove liquiation fee from remaining margin
    liq_fee = int(liq_value * liq_fee_rate)
    margin_remaining = liq_value - liq_fee

    # adjust value for maintenance burn
    idx_mmbr = RiskParameter.MAINTENANCE_MARGIN_BURN_RATE.value
    maintenance_burn = Decimal(mock_market.params(idx_mmbr)) \
        / Decimal(1e18)
    margin_burned = int(margin_remaining * maintenance_burn)
    margin_remaining -= margin_burned

    expect_margin_remaining = int(margin_remaining)

    expect_balance_recipient += expect_margin_remaining
    expect_balance_market -= expect_cost_plus_mint

    actual_balance_recipient = ovl.balanceOf(recipient)
    actual_balance_market = ovl.balanceOf(mock_market)

    assert int(actual_balance_recipient) == approx(
        expect_balance_recipient, rel=1.05e-6)
    assert int(actual_balance_market) == approx(
        expect_balance_market, rel=1.05e-6)


def test_liquidate_floors_value_to_zero_when_position_underwater(mock_market,
                                                                 mock_feed,
                                                                 alice, rando,
                                                                 ovl, factory):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(5.0)
    is_long = True
    price_multiplier = Decimal(0.700)  # close to underwater but not there yet

    # exclude funding for testing edge case
    mock_market.setRiskParam(RiskParameter.K.value, 0, {"from": factory})

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate price to set for liquidation
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    if is_long:
        # longs get the bid on exit, which has e**(-delta) multiplied to it
        # mock feed price should then be liq price * e**(delta) to account
        price_multiplier /= Decimal(1 + tol)
    else:
        # shorts get the ask on exit, which has e**(+delta) multiplied to it
        # mock feed price should then be liq price * e**(-delta) to account
        price_multiplier = 1 / price_multiplier
        price_multiplier *= Decimal(1 + tol)

    price = Decimal(mock_feed.price()) * price_multiplier
    mock_feed.setPrice(price, {"from": rando})

    # priors actual values
    recipient = factory.feeRecipient()
    expect_balance_recipient = ovl.balanceOf(recipient)
    expect_balance_market = ovl.balanceOf(mock_market)
    expect_balance_rando = ovl.balanceOf(rando)

    # calculate position attributes at the current time
    # ignore payoff cap
    liq_cost = Decimal(expect_notional - expect_debt)

    # input values for liquidate
    input_owner = alice.address
    input_pos_id = pos_id

    # liquidate alice's position by rando
    tx = mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # adjust market balance for burned amount
    # check entire cost amount is burned
    expect_mint = - int(liq_cost)
    actual_mint = tx.events["Liquidate"]["mint"]

    assert actual_mint == expect_mint

    expect_balance_market += actual_mint

    # value and fees should floor to zero
    liq_value = 0
    liq_fee = 0

    # calculate expected values
    expect_value = int(liq_value)
    expect_liq_fee = int(liq_fee)

    # check balance of liquidator and recipient doesn't change
    # all initial collateral is burned
    expect_balance_recipient += expect_liq_fee
    expect_balance_market -= expect_value

    actual_balance_recipient = ovl.balanceOf(recipient)
    actual_balance_market = ovl.balanceOf(mock_market)
    actual_balance_rando = ovl.balanceOf(rando)

    assert int(actual_balance_recipient) == approx(expect_balance_recipient)
    assert int(actual_balance_market) == approx(expect_balance_market)
    assert int(actual_balance_rando) == approx(expect_balance_rando)


def test_liquidate_reverts_when_not_position_owner(mock_market, mock_feed,
                                                   alice, bob,
                                                   rando, ovl):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # input values for liquidate
    input_pos_id = pos_id

    # check liquidate reverts when owner is assumed to be bob
    input_owner = bob.address
    with reverts("OVLV1:!position"):
        mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # check liquidate succeeds when owner is specified as alice
    input_owner = alice.address
    mock_market.liquidate(input_owner, input_pos_id, {"from": rando})


def test_liquidate_reverts_when_position_not_exists(mock_market, alice, rando,
                                                    ovl):
    pos_id = 100

    # check liquidate reverts when position does not exist
    with reverts("OVLV1:!position"):
        mock_market.liquidate(alice, pos_id, {"from": rando})


def test_liquidate_reverts_when_position_liquidated(mock_market, mock_feed,
                                                    alice, rando,
                                                    ovl):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    # change price to liq_price so position becomes liquidatable
    mock_feed.setPrice(liq_price, {"from": rando})

    # input values for liquidate
    input_pos_id = pos_id

    # liquidate the position
    input_owner = alice.address
    mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # check attempting to liquidate again reverts
    with reverts("OVLV1:!position"):
        mock_market.liquidate(input_owner, input_pos_id, {"from": rando})


def test_liquidate_reverts_when_position_not_liquidatable(mock_market,
                                                          mock_feed, alice,
                                                          rando, ovl):
    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # tolerance
    tol = 1e-4

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

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
    (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
     expect_is_long, expect_liquidated, expect_oi_shares,
     expect_fraction_remaining) = mock_market.positions(pos_key)

    # calculate the entry and mid prices
    expect_mid_price = tick_to_price(expect_mid_tick)
    expect_entry_price = tick_to_price(expect_entry_tick)

    # mine the chain forward for some time difference with build and liquidate
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after liquidate.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=3600)
    tx = mock_market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)
    expect_oi_initial = Decimal(expect_notional) * \
        Decimal(1e18) / Decimal(expect_mid_price)

    # calculate position attributes at current time, ignore payoff cap
    liq_oi = expect_oi_current
    liq_oi_initial = expect_oi_initial
    liq_notional = Decimal(expect_notional)
    liq_debt = Decimal(expect_debt)

    # calculate expected liquidation price
    # NOTE: p_liq = p_entry * ( MM * OI(0) + D ) / OI if long
    # NOTE:       = p_entry * ( 2 - ( MM * OI(0) + D ) / OI ) if short
    idx_mmf = RiskParameter.MAINTENANCE_MARGIN_FRACTION.value
    idx_liq = RiskParameter.LIQUIDATION_FEE_RATE.value
    maintenance_fraction = Decimal(mock_market.params(idx_mmf)) \
        / Decimal(1e18)
    liq_fee_rate = Decimal(mock_market.params(idx_liq)) / Decimal(1e18)

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)

    mock_feed.setPrice(liq_price, {"from": rando})

    # input values for liquidate
    input_pos_id = pos_id
    input_owner = alice.address

    # check attempting to liquidate position reverts when not liquidatable
    with reverts("OVLV1:!liquidatable"):
        mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # calculate the liquidation price factor
    # then infer market impact required to slip to this price
    # liq_price = entry_price - notional_initial / oi_initial
    #             + (mm * notional_initial + debt) / oi_current
    # liq_price = entry_price + notional_initial / oi_initial
    #             - (mm * notional_initial + debt) / oi_current
    if is_long:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            - liq_notional / liq_oi_initial \
            + (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 - tol)
    else:
        liq_price = Decimal(expect_entry_price) / Decimal(1e18) \
            + liq_notional / liq_oi_initial \
            - (maintenance_fraction * liq_notional / (1-liq_fee_rate)
               + liq_debt) / liq_oi
        liq_price = liq_price * Decimal(1e18) * Decimal(1 + tol)

    mock_feed.setPrice(liq_price, {"from": rando})

    # check can liquidate position when liquidatable
    mock_market.liquidate(input_owner, input_pos_id, {"from": rando})

    # check position has been liquidated
    (_, _, _, _, _, actual_liquidated, actual_oi_shares,
     actual_fraction_remaining) = mock_market.positions(pos_key)
    assert actual_liquidated is True
    assert actual_oi_shares == 0
    assert actual_fraction_remaining == 0


def test_liquidate_reverts_when_has_shutdown(factory, mock_feed, mock_market,
                                             ovl, alice, guardian, rando):
    # build inputs
    input_collateral = int(1e18)
    input_leverage = int(2e18)
    input_is_long = True

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 2**256-1

    # approve market for spending before build. use max
    ovl.approve(mock_market, 2**256 - 1, {"from": alice})

    # build two positions prior to shutdown
    tx_0 = mock_market.build(input_collateral, input_leverage, input_is_long,
                             input_price_limit, {"from": alice})
    tx_1 = mock_market.build(input_collateral, input_leverage, input_is_long,
                             input_price_limit, {"from": alice})

    # cache the pos ids
    input_pos_id_0 = tx_0.return_value
    input_pos_id_1 = tx_1.return_value

    # set price so liquidatable
    liq_price = int(mock_feed.price() / 2.0)
    mock_feed.setPrice(liq_price, {"from": rando})

    # liquidate the first position to check works prior to shutdown
    mock_market.liquidate(alice, input_pos_id_0, {"from": rando})

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(mock_feed, {"from": guardian})

    # attempt to liquidate
    with reverts("OVLV1: shutdown"):
        mock_market.liquidate(alice, input_pos_id_1, {"from": rando})


# TODO: add tests with multiple positions and only one liquidated
