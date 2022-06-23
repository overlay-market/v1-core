import pytest
from brownie import reverts


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
def test_emergency_withdraw(market, factory, ovl, alice):
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
