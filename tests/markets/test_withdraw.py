import pytest
from brownie import reverts


# NOTE: Use isolation fixture to avoid possible revert with max
# NOTE: lev immediately liquidatable market check
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


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


# TODO: test emergency withdraw
