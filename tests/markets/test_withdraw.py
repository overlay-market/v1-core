import pytest
from brownie import chain, reverts
from decimal import Decimal

from .utils import get_position_key


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
        mock_market, mock_feed, factory, ovl, alice, gov, rando):
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
    factory.shutdown(mock_feed, {"from": gov})

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
        mock_market, mock_feed, factory, ovl, alice, gov, rando):
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
    factory.shutdown(mock_feed, {"from": gov})

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
        mock_market, mock_feed, factory, ovl, alice, gov, rando):
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
    factory.shutdown(mock_feed, {"from": gov})

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


# TODO: implement
def test_multiple_emergency_withdraw(market, factory, ovl, alice, bob):
    pass


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
                                                             gov):
    input_pos_id = 100

    # shutdown market
    # NOTE: factory.shutdown() tests in factories/market/test_setters.py
    factory.shutdown(feed, {"from": gov})

    # check can't withdraw collateral when no position exists
    with reverts("OVLV1:!position"):
        market.emergencyWithdraw(input_pos_id, {"from": alice})
