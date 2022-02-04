import pytest
from pytest import approx
from brownie import chain, reverts
from brownie.test import given, strategy
from decimal import Decimal

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
def test_unwind_updates_position(market, feed, alice, ovl, fraction, is_long):
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

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})
    pos_id = tx.return_value

    # get position info
    pos_key = get_position_key(alice.address, pos_id)
    (expect_oi_shares, expect_debt, expect_is_long, expect_liquidated,
     expect_entry_price) = market.positions(pos_key)

    # calculate current oi, debt values of position
    oi_shares = expect_oi_shares/1e18
    oi_total = (market.oiLong()/1e18) if is_long else (market.oiShort()/1e18)
    oi_total_shares = (market.oiLongShares()/1e18) if is_long \
        else (market.oiShortShares()/1e18)
    oi_current = Decimal((oi_shares / oi_total_shares) * oi_total)

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(fraction * Decimal(1e18))

    # unwind fraction of shares
    tx = market.unwind(input_pos_id, input_fraction, {"from": alice})

    # calculate expected exit price
    # NOTE: ask(), bid() tested in test_price.py
    data = feed.latest()
    cap_oi = Decimal(market.capOiAdjustedForBounds(data, market.capOi())/1e18)
    volume = int((oi_current * fraction / cap_oi) * Decimal(1e18))
    price = market.bid(data, volume) if is_long \
        else market.ask(data, volume)

    # calculate expected values
    expect_oi_shares = int(expect_oi_shares * (1 - fraction))
    expect_debt = int(expect_debt * (1 - fraction))
    expect_price = price
    expect_pnl_mag = Decimal(fraction) * oi_current * \
        Decimal(expect_price/expect_entry_price - 1) * Decimal(1e18)
    expect_oi_diff = Decimal(oi_current - oi_initial) * Decimal(1e18)
    expect_mint = int(expect_oi_diff + expect_pnl_mag) if is_long \
        else int(expect_oi_diff - expect_pnl_mag)

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
    assert int(tx.events["Unwind"]["price"]) == approx(expect_price, rel=1e-4)
    # TODO: figure out why rel=1e-2 needed here. because so small?
    assert int(tx.events["Unwind"]["mint"]) == approx(expect_mint, rel=1e-2)


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

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})
    pos_id = tx.return_value

    # check unwind reverts when fraction is zero
    input_fraction = 0
    with reverts("OVLV1:fraction<min"):
        market.unwind(pos_id, input_fraction, {"from": alice})


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

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})
    pos_id = tx.return_value

    # check unwind reverts when fraction is 1 more than 1e18
    input_fraction = 1000000000000000001
    with reverts("OVLV1:fraction>max"):
        market.unwind(pos_id, input_fraction, {"from": alice})

    # check unwind succeeds when fraction is 1e18
    input_fraction = 1000000000000000000
    market.unwind(pos_id, input_fraction, {"from": alice})


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

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})
    pos_id = tx.return_value

    # check unwind reverts when bob attempts
    input_fraction = 1000000000000000000
    with reverts("OVLV1:!position"):
        market.unwind(pos_id, input_fraction, {"from": bob})

    # check unwind succeeds when alice attempts
    market.unwind(pos_id, input_fraction, {"from": alice})


def test_multiple_unwind_unwinds_multiple_positions(market, alice, ovl):
    # get position key/id related info
    # expect_pos_id = market.nextPositionId()

    # loop through 10 times
    n = 10
    collateral = Decimal(1000)
    leverage = Decimal(1.0)
    is_long = True

    # input collateral for each build tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)

    # total approve collateral
    approve_collateral = n * input_collateral * (1 + trading_fee_rate)
    ovl.approve(market, approve_collateral, {"from": alice})

    actual_pos_ids = []
    for i in range(n):
        # NOTE: build() tests in test_build.py
        tx = market.build(input_collateral, input_leverage, input_is_long,
                          {"from": alice})
        pos_id = tx.return_value
        actual_pos_ids.append(pos_id)

    # mine the chain into the future then unwind each
    chain.mine(timedelta=600)

    # unwind all of each position
    fraction = 1e18
    for id in actual_pos_ids:
        tx = market.unwind(id, fraction, {"from": alice})
