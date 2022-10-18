import pytest
from brownie import chain, reverts
from decimal import Decimal
from random import randint

from .utils import get_position_key, RiskParameter


# NOTE: Use isolation fixture to avoid possible revert with max
# NOTE: lev immediately liquidatable market check
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# shutdown tests
def test_shutdown(market, factory, ovl, alice):
    # shutdown the market through factory
    market.shutdown({"from": factory})

    # check bool flips to true
    assert market.isShutdown() is True

    # check can't build anymore
    input_collateral = int(1e18)
    input_leverage = int(1e18)
    input_is_long = True
    input_price_limit = 2**256-1

    # approve market for spending before build. use max
    ovl.approve(market, 2**256 - 1, {"from": alice})
    with reverts("OVLV1: shutdown"):
        market.build(input_collateral, input_leverage, input_is_long,
                     input_price_limit, {"from": alice})

    # check can't shutdown again
    with reverts("OVLV1: shutdown"):
        market.shutdown({"from": factory})


def test_shutdown_reverts_when_not_factory(market, rando):
    with reverts("OVLV1: !factory"):
        market.shutdown({"from": rando})


# emergency withdraw tests
def test_emergency_withdraw_transfers_collateral(
        mock_market, mock_feed, factory, ovl, alice, guardian, rando):
    # input build parameters
    input_collateral = int(1e18)
    input_leverage = int(1e18)
    input_is_long = True
    input_price_limit = 2**256-1

    # approve market for spending before build. use max
    ovl.approve(mock_market, 2**256 - 1, {"from": alice})

    # build a position
    tx = mock_market.build(input_collateral, input_leverage, input_is_long,
                           input_price_limit, {"from": alice})
    input_pos_id = tx.return_value

    # mine chain for funding to occur over timedelta
    chain.mine(timedelta=86400)

    # change price to make the position profitable
    unwind_price = int(mock_feed.price() * Decimal(1.5))
    mock_feed.setPrice(unwind_price, {"from": rando})

    # unwind a portion of position
    fraction = int(0.25e18)
    input_price_limit = 0
    _ = mock_market.unwind(input_pos_id, fraction, input_price_limit,
                           {"from": alice})

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(mock_feed, {"from": guardian})

    expect_collateral_out = int(
        Decimal(input_collateral) * (Decimal(1e18) - Decimal(fraction))
        / Decimal(1e18))

    # cache alice and market balances of ovl prior
    expect_balance_alice = ovl.balanceOf(alice)
    expect_balance_market = ovl.balanceOf(mock_market)

    # emergency withdraw collateral
    tx = mock_market.emergencyWithdraw(input_pos_id, {"from": alice})

    # check alice balance increases by expected withdrawn amount
    expect_collateral_out = min(expect_balance_market, expect_collateral_out)
    expect_balance_alice += expect_collateral_out
    expect_balance_market -= expect_collateral_out

    actual_balance_alice = ovl.balanceOf(alice)
    actual_balance_market = ovl.balanceOf(mock_market)

    # check balances match expectations
    assert actual_balance_alice == expect_balance_alice
    assert actual_balance_market == expect_balance_market

    # check emergency withdraw event
    assert 'EmergencyWithdraw' in tx.events
    assert tx.events["EmergencyWithdraw"]["sender"] == alice.address
    assert tx.events["EmergencyWithdraw"]["positionId"] == input_pos_id
    assert tx.events["EmergencyWithdraw"]["collateral"] \
        == expect_collateral_out


def test_emergency_withdraw_updates_position(
        mock_market, mock_feed, factory, ovl, alice, guardian, rando):
    # input build parameters
    input_collateral = int(1e18)
    input_leverage = int(1e18)
    input_is_long = True
    input_price_limit = 2**256-1

    # approve market for spending before build. use max
    ovl.approve(mock_market, 2**256 - 1, {"from": alice})

    # build a position
    tx = mock_market.build(input_collateral, input_leverage, input_is_long,
                           input_price_limit, {"from": alice})
    input_pos_id = tx.return_value

    # mine chain for funding to occur over timedelta
    chain.mine(timedelta=86400)

    # change price to make the position profitable
    unwind_price = int(mock_feed.price() * Decimal(1.5))
    mock_feed.setPrice(unwind_price, {"from": rando})

    # unwind a portion of position
    fraction = int(0.25e18)
    input_price_limit = 0
    _ = mock_market.unwind(input_pos_id, fraction, input_price_limit,
                           {"from": alice})

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(mock_feed, {"from": guardian})

    # emergency withdraw collateral
    _ = mock_market.emergencyWithdraw(input_pos_id, {"from": alice})

    # check position fraction remaining set to zero
    expect_fraction_remaining = 0

    # get position info
    pos_key = get_position_key(alice.address, input_pos_id)
    (_, _, _, _, _, _, _,
     actual_fraction_remaining) = mock_market.positions(pos_key)

    # check fraction remaining actual set to zero
    assert actual_fraction_remaining == expect_fraction_remaining


def test_emergency_withdraw_executes_transfers(
        mock_market, mock_feed, factory, ovl, alice, guardian, rando):
    # input build parameters
    input_collateral = int(1e18)
    input_leverage = int(1e18)
    input_is_long = True
    input_price_limit = 2**256-1

    # approve market for spending before build. use max
    ovl.approve(mock_market, 2**256 - 1, {"from": alice})

    # build a position
    tx = mock_market.build(input_collateral, input_leverage, input_is_long,
                           input_price_limit, {"from": alice})
    input_pos_id = tx.return_value

    # mine chain for funding to occur over timedelta
    chain.mine(timedelta=86400)

    # change price to make the position profitable
    unwind_price = int(mock_feed.price() * Decimal(1.5))
    mock_feed.setPrice(unwind_price, {"from": rando})

    # unwind a portion of position
    fraction = int(0.25e18)
    input_price_limit = 0
    _ = mock_market.unwind(input_pos_id, fraction, input_price_limit,
                           {"from": alice})

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(mock_feed, {"from": guardian})

    # calculate the expected collateral amount transferred
    expect_collateral_out = int(
        Decimal(input_collateral) * (Decimal(1e18) - Decimal(fraction))
        / Decimal(1e18))

    # emergency withdraw collateral
    tx = mock_market.emergencyWithdraw(input_pos_id, {"from": alice})

    # check events for transfer
    assert 'Transfer' in tx.events
    assert tx.events["Transfer"]["from"] == mock_market.address
    assert tx.events["Transfer"]["to"] == alice.address
    assert tx.events["Transfer"]["value"] == expect_collateral_out


def test_emergency_withdraw_reverts_when_not_shutdown(market, ovl, alice):
    # input build parameters
    input_collateral = int(1e18)
    input_leverage = int(1e18)
    input_is_long = True
    input_price_limit = 2**256-1

    # approve market for spending before build. use max
    ovl.approve(market, 2**256 - 1, {"from": alice})

    # build a position
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      input_price_limit, {"from": alice})
    input_pos_id = tx.return_value

    # check can't withdraw collateral from built position when not shutdown
    with reverts("OVLV1: !shutdown"):
        market.emergencyWithdraw(input_pos_id, {"from": alice})


def test_emergency_withdraw_reverts_when_position_not_exists(market, feed, ovl,
                                                             factory, alice,
                                                             guardian):
    input_pos_id = 100

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(feed, {"from": guardian})

    # check can't withdraw collateral when no position exists
    with reverts("OVLV1:!position"):
        market.emergencyWithdraw(input_pos_id, {"from": alice})


def test_multiple_emergency_withdraw(
        mock_market, mock_feed, factory, ovl, alice, bob, guardian, rando):
    # loop through 10 times
    n = 10
    total_collateral_long = Decimal(10000)
    total_collateral_short = Decimal(7500)

    idx_cap_leverage = RiskParameter.CAP_LEVERAGE.value
    leverage_cap = Decimal(mock_market.params(idx_cap_leverage) / 1e18)

    # approve market for spending then build
    ovl.approve(mock_market, 2**256-1, {"from": alice})
    ovl.approve(mock_market, 2**256-1, {"from": bob})

    # per trade collateral values
    collateral_alice = total_collateral_long / Decimal(n)
    collateral_bob = total_collateral_short / Decimal(n)
    is_long_alice = True
    is_long_bob = False

    actual_pos_ids = []
    for i in range(n):
        chain.mine(timedelta=86400)

        # choose a random leverage
        leverage_alice = randint(1, leverage_cap)
        leverage_bob = randint(1, leverage_cap)

        input_collateral_alice = int(collateral_alice * Decimal(1e18))
        input_collateral_bob = int(collateral_bob * Decimal(1e18))
        input_leverage_alice = int(leverage_alice * Decimal(1e18))
        input_leverage_bob = int(leverage_bob * Decimal(1e18))

        # use max slippage tol so never reverts
        input_price_limit_alice = 2**256-1 if is_long_alice else 0
        input_price_limit_bob = 2**256-1 if is_long_bob else 0

        # build position for alice
        tx_alice = mock_market.build(input_collateral_alice,
                                     input_leverage_alice,
                                     is_long_alice, input_price_limit_alice,
                                     {"from": alice})
        pos_id_alice = tx_alice.return_value

        # build position for bob
        tx_bob = mock_market.build(input_collateral_bob, input_leverage_bob,
                                   is_long_bob, input_price_limit_bob,
                                   {"from": bob})
        pos_id_bob = tx_bob.return_value

        actual_pos_ids.append(pos_id_alice)  # alice ids are even
        actual_pos_ids.append(pos_id_bob)  # bob ids are odd

    # mine the chain into the future then unwind fraction of each
    chain.mine(timedelta=600)

    # set mock price to 10% higher
    price = int(mock_feed.price() * Decimal(1.05))
    mock_feed.setPrice(price, {"from": rando})

    # unwind fractions of each position
    for id in actual_pos_ids:
        # mine the chain forward for some time difference with build and unwind
        # more funding should occur within this interval.
        # NOTE: update() tests in test_update.py
        chain.mine(timedelta=86400)
        _ = mock_market.update({"from": rando})

        # alice is even ids, bob is odd
        is_alice = (id % 2 == 0)
        trader = alice if is_alice else bob

        # choose a random fraction of pos to unwind
        fraction = randint(1, 1e4)  # fraction is only to 1bps precision
        fraction = Decimal(fraction) / Decimal(1e4)
        input_fraction = int(fraction * Decimal(1e18))

        # NOTE: slippage tests in test_slippage.py
        # NOTE: setting to min/max here, so never reverts with slippage>max
        input_price_limit_trader = 0 if is_alice else 2**256-1

        # unwind fraction of position for trader
        _ = mock_market.unwind(id, input_fraction, input_price_limit_trader,
                               {"from": trader})

    # mine the chain into the future then shutdown
    chain.mine(timedelta=600)

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(mock_feed, {"from": guardian})

    # withdraw remaining collateral for each position
    for id in actual_pos_ids:
        # mine the chain forward for some time difference
        chain.mine(timedelta=86400)

        # alice is even ids, bob is odd
        is_alice = (id % 2 == 0)
        trader = alice if is_alice else bob

        # cache position attributes for everything for later comparison
        pos_key = get_position_key(trader.address, id)
        expect_pos = mock_market.positions(pos_key)
        (expect_notional, expect_debt, expect_mid_tick, expect_entry_tick,
         expect_is_long, expect_liquidated, expect_oi_shares,
         expect_fraction_remaining) = expect_pos

        # check revert happens on withdrawal and continue loop
        # if trader has already unwound entire position
        if expect_fraction_remaining == 0:
            with reverts("OVLV1:!position"):
                mock_market.emergencyWithdraw(id, {"from": trader})

            # continue the loop after revert goes through
            continue

        # for other case when position still has collateral left ...
        # cache balances prior to withdraw
        expect_balance_trader = ovl.balanceOf(trader)
        expect_balance_market = ovl.balanceOf(mock_market)

        # calculate amount of collateral expect to be withdrawn
        expect_collateral_out = (expect_notional - expect_debt) * \
            Decimal(expect_fraction_remaining) / Decimal(1e4)

        # withdraw collateral from position
        _ = mock_market.emergencyWithdraw(id, {"from": trader})

        # check fraction remaining set to zero
        actual_pos = mock_market.positions(pos_key)
        (_, _, _, _, _, _, _, actual_fraction_remaining) = actual_pos

        expect_fraction_remaining = 0
        assert actual_fraction_remaining == expect_fraction_remaining

        # adjust expected values for collateral withdrawn out
        expect_collateral_out = min(
            expect_balance_market, expect_collateral_out)
        expect_balance_trader += expect_collateral_out
        expect_balance_market -= expect_collateral_out

        # get balances after withdraw
        actual_balance_trader = ovl.balanceOf(trader)
        actual_balance_market = ovl.balanceOf(mock_market)

        # check balances for market and trader match expectations
        assert actual_balance_trader == expect_balance_trader
        assert actual_balance_market == expect_balance_market
