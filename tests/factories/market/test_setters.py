import pytest
from brownie import chain, reverts
from collections import OrderedDict


# NOTE: Use isolation fixture to avoid possible revert with max
# NOTE: lev immediately liquidatable market check
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# fee recipient tests
def test_set_fee_recipient(factory, gov, rando):
    expect_fee_recipient = rando

    # set fee recipient
    tx = factory.setFeeRecipient(expect_fee_recipient, {"from": gov})

    # check fee recipient changed
    actual_fee_recipient = factory.feeRecipient()
    assert expect_fee_recipient == actual_fee_recipient

    # check event emitted
    assert 'FeeRecipientUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "recipient": rando
    })
    actual_event = tx.events['FeeRecipientUpdated']
    assert actual_event == expect_event


def test_set_fee_recipient_reverts_when_not_gov(factory, alice):
    expect_fee_recipient = alice

    # check can't set fee recipient with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setFeeRecipient(expect_fee_recipient, {"from": alice})


def test_set_fee_recipient_reverts_when_zero_address(factory, gov):
    expect_fee_recipient = "0x0000000000000000000000000000000000000000"

    # check can't set fee recipient as zero address
    with reverts("OVLV1: feeRecipient should not be zero address"):
        _ = factory.setFeeRecipient(expect_fee_recipient, {"from": gov})


# risk param tests
def test_set_risk_param(factory, market, gov):
    feed = market.feed()

    # default risk params
    default_params = [
        1200000000000,  # expect_k
        500000000000000000,  # expect_lmbda
        1500000000000000,  # expect_delta
        10000000000000000000,  # expect_cap_payoff
        700000000000000000000000,  # expect_cap_notional
        3000000000000000000,  # expect_cap_leverage
        3592000,  # expect_circuit_breaker_window
        86670000000000000000000,  # expect_circuit_breaker_mint_target
        12500000000000000,  # expect_maintenance_margin_fraction
        200000000000000000,  # expect_maintenance_margin_burn_rate
        20000000000000000,  # expect_liquidation_fee_rate
        550000000000000,  # expect_trading_fee_rate
        200000000000000,  # expect_min_collateral
        12000000000000,  # expect_price_drift_upper_limit
        14,  # expect_average_block_time
    ]

    for i in range(len(default_params)):
        # set param
        expect_param = default_params[i]
        tx = factory.setRiskParam(feed, i, expect_param, {"from": gov})

        # check param changed
        actual_param = market.params(i)
        assert expect_param == actual_param

        # check event emitted
        assert 'ParamUpdated' in tx.events
        expect_event = OrderedDict({
            "user": gov,
            "market": market,
            "name": i,
            "value": expect_param
        })
        actual_event = tx.events['ParamUpdated']
        assert actual_event == expect_event


def test_set_risk_param_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_k = 361250000000

    # check can't set k with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setRiskParam(feed, 0, expect_k, {"from": alice})


def test_set_risk_param_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()

    for i in range(15):
        expect_param = factory.PARAMS_MIN(i) - 1

        if expect_param >= 0:
            # check can't set param less than min
            with reverts("OVLV1: param out of bounds"):
                _ = factory.setRiskParam(feed, i, expect_param, {"from": gov})

        # check can set param when equal to min
        expect_param = factory.PARAMS_MIN(i)
        factory.setRiskParam(feed, i, expect_param, {"from": gov})

        actual_param = market.params(i)
        assert actual_param == expect_param

        # undo the tx so can start form conftest.py market state
        chain.undo()


def test_set_risk_param_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()

    for i in range(15):
        expect_param = factory.PARAMS_MAX(i) + 1

        # check can't set param greater than max
        with reverts("OVLV1: param out of bounds"):
            _ = factory.setRiskParam(feed, i, expect_param, {"from": gov})

        # check can set param when equal to max
        expect_param = factory.PARAMS_MAX(i)
        factory.setRiskParam(feed, i, expect_param, {"from": gov})

        actual_param = market.params(i)
        assert actual_param == expect_param

        # undo the tx so can start form conftest.py market state
        chain.undo()


# shutdown tests
def test_shutdown(factory, market, guardian):
    feed = market.feed()

    # check hasn't been shut down yet
    assert market.isShutdown() is False

    # shut the market down
    tx = factory.shutdown(feed, {"from": guardian})

    # check now set to shutdown
    market.isShutdown() is True

    # check event emitted
    assert 'EmergencyShutdown' in tx.events
    expect_event = OrderedDict({
        "user": guardian,
        "market": market
    })
    actual_event = tx.events['EmergencyShutdown']
    assert actual_event == expect_event


def test_shutdown_reverts_when_not_guardian(factory, market, rando):
    feed = market.feed()

    # can't shutdown when not a guardian
    with reverts("OVLV1: !guardian"):
        _ = factory.shutdown(feed, {"from": rando})
