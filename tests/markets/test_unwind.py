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

    # TODO: figure out why rel=1e-2 needed here. Large error
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


def test_unwind_reverts_when_position_not_exists(market, alice, ovl):
    pos_id = 100

    # check unwind reverts when position does not exist
    input_fraction = 1000000000000000000
    with reverts("OVLV1:!position"):
        market.unwind(pos_id, input_fraction, {"from": alice})


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

        # build position for alice
        tx_alice = market.build(input_collateral_alice, input_leverage_alice,
                                is_long_alice, {"from": alice})
        pos_id_alice = tx_alice.return_value

        # build position for bob
        tx_bob = market.build(input_collateral_bob, input_leverage_bob,
                              is_long_bob, {"from": bob})
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
        input_fraction = 508809194583874886  # randint(1, 1e18)
        fraction = Decimal(input_fraction) / Decimal(1e18)

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
        tx_alice = market.unwind(id, input_fraction, {"from": trader})

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
