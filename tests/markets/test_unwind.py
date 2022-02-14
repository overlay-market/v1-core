import pytest
from pytest import approx
from brownie import chain, reverts
from brownie.test import given, strategy
from decimal import Decimal
from random import randint

from .utils import calculate_position_info, get_position_key


# NOTE: Tests passing with isolation fixture
# TODO: Fix tests to pass even without isolation fixture (?)
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_updates_position(market, feed, alice, rando, ovl,
                                 fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    tx = market.update({"from": rando})
    data = tx.return_value

    # calculate current oi, debt values of position
    expect_total_oi = market.oiLong() if is_long \
        else market.oiShort()
    expect_total_oi_shares = market.oiLongShares() if is_long \
        else market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_oi = fraction * expect_oi_current
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)
    unwound_debt = fraction * Decimal(expect_debt)
    unwound_collateral = unwound_oi - unwound_debt

    # calculate expected exit price
    cap_oi = Decimal(market.capOiAdjustedForBounds(data, market.capOi()))
    volume = int((unwound_oi / cap_oi) * Decimal(1e18))
    expect_exit_price = market.bid(data, volume) if is_long \
        else market.ask(data, volume)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})

    # adjust oi shares, debt position expected attributes downward for unwind
    expect_oi_shares = int(expect_oi_shares * (1 - fraction))
    expect_debt = int(expect_debt * (1 - fraction))

    # check expected pos attributes match actual after unwind
    (actual_oi_shares, actual_debt, actual_is_long, actual_liquidated,
     actual_entry_price) = market.positions(pos_key)

    assert int(actual_oi_shares) == approx(expect_oi_shares)
    assert int(actual_debt) == approx(expect_debt)
    assert actual_is_long == expect_is_long
    assert actual_liquidated == expect_liquidated
    assert actual_entry_price == expect_entry_price

    # check unwind event with expected values
    assert "Unwind" in tx.events
    assert tx.events["Unwind"]["sender"] == alice.address
    assert tx.events["Unwind"]["positionId"] == pos_id
    assert tx.events["Unwind"]["fraction"] == input_fraction

    actual_exit_price = int(tx.events["Unwind"]["price"])
    assert actual_exit_price == approx(expect_exit_price, rel=1e-3)

    # calculate expected values for mint comparison
    unwound_pnl = unwound_oi * \
        (Decimal(actual_exit_price) / Decimal(expect_entry_price) - 1)
    if not is_long:
        unwound_pnl *= -1

    expect_value = int(unwound_collateral + unwound_pnl)
    expect_cost = int(unwound_cost)
    expect_mint = expect_value - expect_cost

    # TODO: why do we need 1e-2 for tolerance here? Uniswap mainnet-fork moves?
    actual_mint = int(tx.events["Unwind"]["mint"])
    assert actual_mint == approx(expect_mint, rel=1e-2)


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_removes_oi(market, feed, alice, rando, ovl,
                           fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    _ = market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = market.oiLong() if is_long else market.oiShort()
    expect_total_oi_shares = market.oiLongShares() if is_long \
        else market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # calculate expected oi, debt removed
    unwound_oi = int(fraction * expect_oi_current)
    unwound_oi_shares = int(fraction * Decimal(expect_oi_shares))

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})

    # adjust total oi and total oi shares downward for unwind
    expect_total_oi -= unwound_oi
    expect_total_oi_shares -= unwound_oi_shares

    # check expected total oi and oi shares on side match actual
    actual_total_oi = market.oiLong() if is_long else market.oiShort()
    actual_total_oi_shares = market.oiLongShares() \
        if is_long else market.oiShortShares()

    assert int(actual_total_oi) == approx(expect_total_oi, rel=1e-4)
    assert int(actual_total_oi_shares) == approx(expect_total_oi_shares,
                                                 rel=1e-4)


def test_unwind_updates_market(market, alice, ovl):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)
    fraction = Decimal(1.0)
    is_long = True

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # cache prior timestamp update last value
    prior_timestamp_update_last = market.timestampUpdateLast()

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval
    chain.mine(timedelta=600)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})

    # get the expected timestamp and check equal to actual
    expect_timestamp_update_last = chain[tx.block_number]['timestamp']
    actual_timestamp_update_last = market.timestampUpdateLast()

    assert actual_timestamp_update_last == expect_timestamp_update_last
    assert actual_timestamp_update_last != prior_timestamp_update_last


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_registers_volume(market, feed, alice, rando, ovl,
                                 fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    _ = market.update({"from": rando})

    # priors actual values. longs get the bid, shorts get the ask on unwind
    snapshot_volume = market.snapshotVolumeBid() if is_long \
        else market.snapshotVolumeAsk()
    last_timestamp, last_window, last_volume = snapshot_volume

    last_total_oi = market.oiLong() if is_long \
        else market.oiShort()
    last_total_oi_shares = market.oiLongShares() if is_long \
        else market.oiShortShares()
    last_pos_oi = (last_total_oi * expect_oi_shares) / last_total_oi_shares

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})

    # calculate expected rolling volume and window numbers when
    # adjusted for decay
    # NOTE: decayOverWindow() tested in test_rollers.py
    data = feed.latest()
    _, micro_window, _, _, _, _, _, _ = data

    oi = fraction * Decimal(last_pos_oi)
    cap_oi = Decimal(market.capOiAdjustedForBounds(data, market.capOi()))

    input_volume = int((oi / cap_oi) * Decimal(1e18))
    input_window = micro_window
    input_timestamp = chain[tx.block_number]['timestamp']

    # expect accumulator now to be calculated as
    # accumulatorLast * (1 - dt/windowLast) + value
    dt = input_timestamp - last_timestamp
    last_volume_decayed = last_volume * (1 - dt/last_window) \
        if last_window != 0 and dt >= last_window else 0
    expect_volume = int(last_volume_decayed + input_volume)

    # expect window now to be calculated as weighted average
    # of remaining time left in last window and total time in new window
    # weights are accumulator values for the respective time window
    numerator = int((last_window - dt) * last_volume_decayed
                    + input_window * input_volume)
    expect_window = int(numerator / expect_volume)
    expect_timestamp = input_timestamp

    # compare with actual rolling volume, timestamp last, window last values
    actual = market.snapshotVolumeBid() if is_long else \
        market.snapshotVolumeAsk()
    actual_timestamp, actual_window, actual_volume = actual

    assert actual_timestamp == expect_timestamp
    assert int(actual_window) == approx(expect_window, abs=1)  # tol to 1s
    assert int(actual_volume) == approx(expect_volume, rel=1e-4)


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_registers_mint(market, feed, alice, rando, ovl,
                               fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    _ = market.update({"from": rando})

    # priors actual values for snapshot of minted roller
    snapshot_minted = market.snapshotMinted()
    last_timestamp, last_window, last_minted = snapshot_minted

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})
    actual_mint = tx.events["Unwind"]["mint"]

    # calculate expected rolling minted and window numbers when
    # adjusted for decay
    # NOTE: decayOverWindow() tested in test_rollers.py
    input_minted = int(actual_mint)
    input_window = int(market.circuitBreakerWindow())
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
    expect_window = int(numerator /
                        (abs(last_minted_decayed) + abs(input_minted)))
    expect_timestamp = input_timestamp

    # compare with actual rolling minted, timestamp last, window last values
    actual = market.snapshotMinted()
    actual_timestamp, actual_window, actual_minted = actual

    assert actual_timestamp == expect_timestamp
    assert int(actual_window) == approx(expect_window, abs=1)  # tol to 1s
    assert int(actual_minted) == approx(expect_minted, rel=1e-4)


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_executes_transfers(market, feed, alice, rando, ovl,
                                   fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    _ = market.update({"from": rando})

    # calculate current oi, debt values of position
    expect_total_oi = market.oiLong() if is_long else market.oiShort()
    expect_total_oi_shares = market.oiLongShares() if is_long \
        else market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})

    # get expected exit price
    price = tx.events["Unwind"]["price"]

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_oi = fraction * expect_oi_current
    unwound_debt = fraction * Decimal(expect_debt)
    unwound_collateral = unwound_oi - unwound_debt
    unwound_pnl = unwound_oi * (Decimal(price) / Decimal(expect_entry_price)
                                - 1)
    unwound_value = unwound_collateral + unwound_pnl if is_long \
        else unwound_collateral - unwound_pnl
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)

    unwound_notional = unwound_value + unwound_debt
    unwound_trading_fee = unwound_notional * \
        (Decimal(market.tradingFeeRate()) / Decimal(1e18))
    if unwound_trading_fee > unwound_value:
        unwound_trading_fee = unwound_value

    # calculate expected values
    expect_mint = int(unwound_value - unwound_cost)

    # check expected pnl in line with Unwind event first
    assert int(tx.events["Unwind"]["mint"]) == approx(expect_mint, rel=1e-2)

    # Examine transfer event to verify mint or burn happened
    # if expect_mint > 0, should have a mint with Transfer event
    # If expect_mint < 0, should have a burn with Transfer event
    minted = expect_mint > 0
    expect_mint_from = "0x0000000000000000000000000000000000000000" if minted \
        else market.address
    expect_mint_to = market.address if minted \
        else "0x0000000000000000000000000000000000000000"
    expect_mint_mag = abs(expect_mint)

    # value less fees expected
    expect_value_out = int(unwound_value - unwound_trading_fee)

    # trading fee expected
    expect_trade_fee = int(unwound_trading_fee)

    # check Transfer events for:
    # 1. mint or burn of pnl; 2. value less trade fees out; 3. trade fees out
    assert 'Transfer' in tx.events
    assert len(tx.events['Transfer']) == 3

    # check actual amount minted or burned is in line with expected (1)
    assert tx.events["Transfer"][0]["from"] == expect_mint_from
    assert tx.events["Transfer"][0]["to"] == expect_mint_to
    assert int(tx.events["Transfer"][0]["value"]) == approx(expect_mint_mag,
                                                            rel=1e-2)

    # check unwind event has same value for pnl as transfer event (1)
    actual_transfer_mint = tx.events["Transfer"][0]["value"] if minted \
        else -tx.events["Transfer"][0]["value"]
    assert tx.events["Unwind"]["mint"] == actual_transfer_mint

    # check value less fees in event (2)
    assert tx.events['Transfer'][1]['from'] == market.address
    assert tx.events['Transfer'][1]['to'] == alice.address
    assert int(tx.events['Transfer'][1]['value']) == \
        approx(expect_value_out, rel=1e-4)

    # check value less trade fees out (3)
    assert tx.events['Transfer'][2]['from'] == market.address
    assert tx.events['Transfer'][2]['to'] == market.feeRecipient()
    assert int(tx.events['Transfer'][2]['value']) == approx(expect_trade_fee,
                                                            rel=1e-4)


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_transfers_value_to_trader(market, feed, alice, rando, ovl,
                                          fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    tx = market.update({"from": rando})

    # priors actual values
    expect_balance_alice = ovl.balanceOf(alice)
    expect_balance_market = ovl.balanceOf(market)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)
    unwound_debt = fraction * Decimal(expect_debt)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})
    actual_mint = tx.events["Unwind"]["mint"]
    expect_balance_market += actual_mint

    # calculate expected values
    expect_value = int(unwound_cost + actual_mint)
    expect_notional = int(expect_value + unwound_debt)
    expect_trade_fee = int(Decimal(expect_notional)
                           * Decimal(market.tradingFeeRate()) / Decimal(1e18))
    if expect_trade_fee > expect_value:
        expect_trade_fee = expect_value

    expect_value_out = expect_value - expect_trade_fee

    expect_balance_alice += expect_value_out
    expect_balance_market -= expect_value

    actual_balance_alice = ovl.balanceOf(alice)
    actual_balance_market = ovl.balanceOf(market)

    assert int(actual_balance_alice) == approx(expect_balance_alice)
    assert int(actual_balance_market) == approx(expect_balance_market)


@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'))
def test_unwind_transfers_trading_fees(market, feed, alice, rando, ovl,
                                       fraction, is_long):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # mine the chain forward for some time difference with build and unwind
    # funding should occur within this interval.
    # Use update() to update state to query values for checks vs expected
    # after unwind.
    # NOTE: update() tests in test_update.py
    chain.mine(timedelta=600)
    tx = market.update({"from": rando})

    # priors actual values
    recipient = market.feeRecipient()
    expect_balance_recipient = ovl.balanceOf(recipient)
    expect_balance_market = ovl.balanceOf(market)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)
    unwound_debt = fraction * Decimal(expect_debt)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, input_price_limit,
                       {"from": alice})
    actual_mint = tx.events["Unwind"]["mint"]
    expect_balance_market += actual_mint

    # calculate expected values
    expect_value = int(unwound_cost + actual_mint)
    expect_notional = int(expect_value + unwound_debt)
    expect_trade_fee = int(Decimal(expect_notional)
                           * Decimal(market.tradingFeeRate()) / Decimal(1e18))
    if expect_trade_fee > expect_value:
        expect_trade_fee = expect_value

    expect_balance_recipient += expect_trade_fee
    expect_balance_market -= expect_value

    actual_balance_recipient = ovl.balanceOf(recipient)
    actual_balance_market = ovl.balanceOf(market)

    assert int(actual_balance_recipient) == approx(expect_balance_recipient)
    assert int(actual_balance_market) == approx(expect_balance_market)


# NOTE: use mock market to change exit price to whatever
@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'),
    price_multiplier=strategy('decimal', min_value='1.100', max_value='5.000',
                              places=3))
def test_unwind_mints_when_profitable(mock_market, mock_feed,
                                      alice, rando,
                                      ovl, fraction, is_long,
                                      price_multiplier):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

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
    _ = mock_market.update({"from": rando})

    # change price by factor
    price = mock_feed.price() * price_multiplier if is_long \
        else mock_feed.price() / price_multiplier
    mock_feed.setPrice(price)

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_oi = fraction * expect_oi_current
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)
    unwound_debt = fraction * Decimal(expect_debt)
    unwound_collateral = unwound_oi - unwound_debt

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = mock_market.unwind(input_pos_id, input_fraction, input_price_limit,
                            {"from": alice})
    expect_exit_price = tx.events["Unwind"]['price']

    unwound_pnl = unwound_oi * \
        (Decimal(expect_exit_price) / Decimal(expect_entry_price) - 1)
    if not is_long:
        unwound_pnl *= -1

    # calculate expected values
    expect_value = int(unwound_collateral + unwound_pnl)
    expect_cost = int(unwound_cost)
    expect_mint = expect_value - expect_cost

    # check tx events have a mint to the mock market address
    assert tx.events["Transfer"][0]['from'] \
        == "0x0000000000000000000000000000000000000000"
    assert tx.events["Transfer"][0]['to'] == mock_market.address
    assert int(tx.events["Transfer"][0]['value']) == approx(expect_mint,
                                                            rel=1e-4)


# TODO: test profits when greater than cap


# NOTE: use mock market to change exit price to whatever
@given(
    fraction=strategy('decimal', min_value='0.001', max_value='1.000',
                      places=3),
    is_long=strategy('bool'),
    price_multiplier=strategy('decimal', min_value='1.100', max_value='5.000',
                              places=3))
def test_unwind_burns_when_not_profitable(mock_market, mock_feed,
                                          alice, rando,
                                          ovl, fraction, is_long,
                                          price_multiplier):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)

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
    _ = mock_market.update({"from": rando})

    # change price by factor
    price = mock_feed.price() * price_multiplier if not is_long \
        else mock_feed.price() / price_multiplier
    mock_feed.setPrice(price)

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_oi = fraction * expect_oi_current
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)
    unwound_debt = fraction * Decimal(expect_debt)
    unwound_collateral = unwound_oi - unwound_debt

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = mock_market.unwind(input_pos_id, input_fraction, input_price_limit,
                            {"from": alice})
    expect_exit_price = tx.events["Unwind"]['price']

    unwound_pnl = unwound_oi * \
        (Decimal(expect_exit_price) / Decimal(expect_entry_price) - 1)
    if not is_long:
        unwound_pnl *= -1

    # calculate expected values
    expect_value = int(unwound_collateral + unwound_pnl)
    if expect_value < 0:
        # in case position went underwater, value should floor to zero
        expect_value = 0

    expect_cost = int(unwound_cost)
    expect_burn = expect_cost - expect_value

    # check tx events have a burn from the mock market address
    assert tx.events["Transfer"][0]['from'] == mock_market.address
    assert tx.events["Transfer"][0]['to'] \
        == "0x0000000000000000000000000000000000000000"
    assert int(tx.events["Transfer"][0]['value']) == approx(expect_burn,
                                                            rel=1e-4)


# test for trading fee edge case of tradingFee > value
def test_unwind_transfers_fees_when_fees_greater_than_value(mock_market,
                                                            mock_feed, alice,
                                                            factory, rando,
                                                            ovl):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(5.0)
    is_long = True
    fraction = Decimal(1.0)
    price_multiplier = Decimal(0.8065)  # close to underwater but not there yet

    # exclude funding for testing edge case of fees > value
    mock_market.setK(0, {"from": factory})

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
    _ = mock_market.update({"from": rando})

    # priors actual values
    recipient = mock_market.feeRecipient()
    expect_balance_recipient = ovl.balanceOf(recipient)
    expect_balance_market = ovl.balanceOf(mock_market)
    expect_balance_alice = ovl.balanceOf(alice)

    # change price by factor
    price = mock_feed.price() * price_multiplier if is_long \
        else mock_feed.price() / price_multiplier
    mock_feed.setPrice(price)

    # calculate current oi, debt values of position
    expect_total_oi = mock_market.oiLong() if is_long \
        else mock_market.oiShort()
    expect_total_oi_shares = mock_market.oiLongShares() if is_long \
        else mock_market.oiShortShares()
    expect_oi_current = (Decimal(expect_total_oi)*Decimal(expect_oi_shares)) \
        / Decimal(expect_total_oi_shares)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_oi = fraction * expect_oi_current
    unwound_debt = fraction * Decimal(expect_debt)
    unwound_collateral = unwound_oi - unwound_debt

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = mock_market.unwind(input_pos_id, input_fraction, input_price_limit,
                            {"from": alice})

    # get exit price
    expect_exit_price = tx.events["Unwind"]['price']

    # adjust market balance for burned amount
    actual_mint = tx.events["Unwind"]["mint"]
    expect_balance_market += actual_mint

    unwound_pnl = unwound_oi * \
        (Decimal(expect_exit_price) / Decimal(expect_entry_price) - 1)
    if not is_long:
        unwound_pnl *= -1

    # since notional * fee < value, trading_fee should equal value
    unwound_value = unwound_collateral + unwound_pnl
    unwound_trading_fee = unwound_value

    # calculate expected values
    expect_value = int(unwound_value)
    expect_trade_fee = int(unwound_trading_fee)

    # check balance of trader doesn't change but recipient gets fee
    expect_balance_recipient += expect_trade_fee
    expect_balance_market -= expect_value

    actual_balance_recipient = ovl.balanceOf(recipient)
    actual_balance_market = ovl.balanceOf(mock_market)
    actual_balance_alice = ovl.balanceOf(alice)

    assert int(actual_balance_recipient) == approx(expect_balance_recipient)
    assert int(actual_balance_market) == approx(expect_balance_market)
    assert int(actual_balance_alice) == approx(expect_balance_alice)


# test for when value is underwater and unwind
def test_unwind_floors_value_to_zero_when_underwater(mock_market,
                                                     mock_feed, alice,
                                                     rando, ovl, factory):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(5.0)
    is_long = True
    fraction = Decimal(1.0)
    price_multiplier = Decimal(0.700)  # close to underwater but not there yet

    # exclude funding for testing edge case of fees > value
    mock_market.setK(0, {"from": factory})

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
    _ = mock_market.update({"from": rando})

    # priors actual values
    recipient = mock_market.feeRecipient()
    expect_balance_recipient = ovl.balanceOf(recipient)
    expect_balance_market = ovl.balanceOf(mock_market)
    expect_balance_alice = ovl.balanceOf(alice)

    # change price by factor
    price = mock_feed.price() * price_multiplier if is_long \
        else mock_feed.price() / price_multiplier
    mock_feed.setPrice(price)

    # calculate position attributes at the current time for fraction
    # ignore payoff cap
    unwound_cost = fraction * Decimal(expect_oi_shares - expect_debt)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # unwind fraction of shares
    tx = mock_market.unwind(input_pos_id, input_fraction, input_price_limit,
                            {"from": alice})

    # adjust market balance for burned amount
    # check entire cost amount is burned
    expect_mint = - int(unwound_cost)
    actual_mint = tx.events["Unwind"]["mint"]
    assert actual_mint == expect_mint

    expect_balance_market += actual_mint

    # value and fees should floor to zero
    unwound_value = 0
    unwound_trading_fee = 0

    # calculate expected values
    expect_value = int(unwound_value)
    expect_trade_fee = int(unwound_trading_fee)

    # check balance of trader and recipient doesn't change
    # all initial collateral is burned
    expect_balance_recipient += expect_trade_fee
    expect_balance_market -= expect_value

    actual_balance_recipient = ovl.balanceOf(recipient)
    actual_balance_market = ovl.balanceOf(mock_market)
    actual_balance_alice = ovl.balanceOf(alice)

    assert int(actual_balance_recipient) == approx(expect_balance_recipient)
    assert int(actual_balance_market) == approx(expect_balance_market)
    assert int(actual_balance_alice) == approx(expect_balance_alice)


def test_unwind_reverts_when_fraction_zero(market, alice, ovl):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # check unwind reverts when fraction is zero
    input_fraction = 0
    with reverts("OVLV1:fraction<min"):
        market.unwind(pos_id, input_fraction, input_price_limit,
                      {"from": alice})


def test_unwind_reverts_when_fraction_greater_than_one(market, alice, ovl):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # check unwind reverts when fraction is 1 more than 1e18
    input_fraction = 1000000000000000001
    with reverts("OVLV1:fraction>max"):
        market.unwind(pos_id, input_fraction, input_price_limit,
                      {"from": alice})

    # check unwind succeeds when fraction is 1e18
    input_fraction = 1000000000000000000
    market.unwind(pos_id, input_fraction, input_price_limit, {"from": alice})


def test_unwind_reverts_when_not_position_owner(market, alice, bob, ovl):
    # position build attributes
    oi_initial = Decimal(1000)
    leverage = Decimal(1.5)
    is_long = True

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
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
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0 if is_long else 2**256-1

    # check unwind reverts when bob attempts
    input_fraction = 1000000000000000000
    with reverts("OVLV1:!position"):
        market.unwind(pos_id, input_fraction, input_price_limit, {"from": bob})

    # check unwind succeeds when alice attempts
    market.unwind(pos_id, input_fraction, input_price_limit, {"from": alice})


def test_unwind_reverts_when_position_not_exists(market, alice, ovl):
    pos_id = 100

    # check unwind reverts when position does not exist
    input_fraction = 1000000000000000000
    with reverts("OVLV1:!position"):
        market.unwind(pos_id, input_fraction, 0, {"from": alice})


# TODO: test_unwind_reverts_when_position_liquidated():


def test_multiple_unwind_unwinds_multiple_positions(market, factory, ovl,
                                                    alice, bob):
    # loop through 10 times
    n = 10
    total_oi_long = Decimal(10000)
    total_oi_short = Decimal(7500)

    # set k to zero to avoid funding calcs
    market.setK(0, {"from": factory})

    # alice goes long and bob goes short n times
    input_total_oi_long = total_oi_long * Decimal(1e18)
    input_total_oi_short = total_oi_short * Decimal(1e18)

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    leverage_cap = Decimal(market.capLeverage() / 1e18)

    # approve collateral amount: collateral + trade fee
    approve_collateral_alice = int((input_total_oi_long *
                                    (1 + trading_fee_rate)))
    approve_collateral_bob = int((input_total_oi_short *
                                  (1 + trading_fee_rate)))

    # approve market for spending then build
    ovl.approve(market, approve_collateral_alice, {"from": alice})
    ovl.approve(market, approve_collateral_bob, {"from": bob})

    # per trade oi values
    oi_alice = total_oi_long / Decimal(n)
    oi_bob = total_oi_short / Decimal(n)
    is_long_alice = True
    is_long_bob = False

    actual_pos_ids = []
    for i in range(n):
        chain.mine(timedelta=60)

        # choose a random leverage
        leverage_alice = randint(1, leverage_cap)
        leverage_bob = randint(1, leverage_cap)

        # calculate collateral amounts
        collateral_alice, _, debt_alice, _ = calculate_position_info(
            oi_alice, leverage_alice, trading_fee_rate)
        collateral_bob, _, debt_bob, _ = calculate_position_info(
            oi_bob, leverage_bob, trading_fee_rate)

        input_collateral_alice = int(collateral_alice * Decimal(1e18))
        input_collateral_bob = int(collateral_bob * Decimal(1e18))
        input_leverage_alice = int(leverage_alice * Decimal(1e18))
        input_leverage_bob = int(leverage_bob * Decimal(1e18))

        # NOTE: slippage tests in test_slippage.py
        # NOTE: setting to min/max here, so never reverts with slippage>max
        input_price_limit_alice = 2**256-1 if is_long_alice else 0
        input_price_limit_bob = 2**256-1 if is_long_bob else 0

        # build position for alice
        tx_alice = market.build(input_collateral_alice, input_leverage_alice,
                                is_long_alice, input_price_limit_alice,
                                {"from": alice})
        pos_id_alice = tx_alice.return_value

        # build position for bob
        tx_bob = market.build(input_collateral_bob, input_leverage_bob,
                              is_long_bob, input_price_limit_bob,
                              {"from": bob})
        pos_id_bob = tx_bob.return_value

        actual_pos_ids.append(pos_id_alice)  # alice ids are even
        actual_pos_ids.append(pos_id_bob)  # bob ids are odd

    # mine the chain into the future then unwind each
    chain.mine(timedelta=600)

    # unwind fractions of each position
    for id in actual_pos_ids:
        chain.mine(timedelta=60)

        # alice is even ids, bob is odd
        is_alice = (id % 2 == 0)
        trader = alice if is_alice else bob

        # choose a random fraction of pos to unwind
        input_fraction = randint(1, 1e18)
        fraction = Decimal(input_fraction) / Decimal(1e18)

        # NOTE: slippage tests in test_slippage.py
        # NOTE: setting to min/max here, so never reverts with slippage>max
        input_price_limit_trader = 0 if is_alice else 2**256-1

        # cache current aggregate oi and oi shares for comparison later
        total_oi = market.oiLong() if is_alice else market.oiShort()
        total_oi_shares = market.oiLongShares() if is_alice \
            else market.oiShortShares()

        # cache position attributes for everything for later comparison
        pos_key = get_position_key(trader.address, id)
        expect_pos = market.positions(pos_key)
        (expect_oi_shares, expect_debt, expect_is_long,
         expect_liquidated, expect_entry_price) = expect_pos

        # unwind fraction of position for trader
        _ = market.unwind(id, input_fraction, input_price_limit_trader,
                          {"from": trader})

        # get updated actual position attributes
        actual_pos = market.positions(pos_key)
        (actual_oi_shares, actual_debt, actual_is_long,
         actual_liquidated, actual_entry_price) = actual_pos

        # check position info for id has decreased position oi, debt
        expect_oi_shares_unwound = int(expect_oi_shares * fraction)
        expect_oi_unwound = int(expect_oi_shares_unwound * total_oi
                                / total_oi_shares)

        expect_oi_shares = int(expect_oi_shares * (1 - fraction))
        expect_debt = int(expect_debt * (1 - fraction))

        assert int(actual_oi_shares) == approx(expect_oi_shares)
        assert int(actual_debt) == approx(expect_debt)
        assert actual_is_long == expect_is_long
        assert actual_liquidated == expect_liquidated
        assert actual_entry_price == expect_entry_price

        # check aggregate oi and oi shares on side have decreased
        expect_total_oi = total_oi - expect_oi_unwound
        expect_total_oi_shares = total_oi_shares - expect_oi_shares_unwound

        actual_total_oi = market.oiLong() if is_alice else market.oiShort()
        actual_total_oi_shares = market.oiLongShares() if is_alice \
            else market.oiShortShares()

        assert int(actual_total_oi) == approx(expect_total_oi)
        assert int(actual_total_oi_shares) == approx(expect_total_oi_shares)
