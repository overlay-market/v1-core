from collections import OrderedDict


# k tests
def test_set_k(factory, market, gov):
    feed = market.feed()
    print('actual_k (prior)', market.k())
    expect_k = 3612500000000
    print('expect_k', expect_k)
    print('feed', feed)
    # set k
    tx = factory.setK(feed, expect_k, {"from": gov})

    # check k changed
    actual_k = market.k()
    print('actual_k', actual_k)
    assert expect_k == actual_k

    # check event emitted
    assert 'FundingUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "k": expect_k
    })
    actual_event = tx.events['FundingUpdated']
    assert actual_event == expect_event


def test_set_k_reverts_when_not_gov(factory, alice):
    pass


def test_set_k_reverts_when_less_than_min(factory, alice):
    pass


def test_set_k_reverts_when_greater_than_max(factory, alice):
    pass


# lmbda tests
def test_set_lmbda(factory, market, gov):
    pass


def test_set_lmbda_reverts_when_not_gov(factory, alice):
    pass


def test_set_lmbda_reverts_when_less_than_min(factory, alice):
    pass


def test_set_lmbda_reverts_when_greater_than_max(factory, alice):
    pass


# delta tests
def test_set_delta(factory, market, gov):
    pass


def test_set_delta_reverts_when_not_gov(factory, alice):
    pass


def test_set_delta_reverts_when_less_than_min(factory, alice):
    pass


def test_set_delta_reverts_when_greater_than_max(factory, alice):
    pass


# capPayoff tests
def test_set_cap_payoff(factory, market, gov):
    pass


def test_set_cap_payoff_reverts_when_not_gov(factory, alice):
    pass


def test_set_cap_payoff_reverts_when_less_than_min(factory, alice):
    pass


def test_set_cap_payoff_reverts_when_greater_than_max(factory, alice):
    pass


# capLeverage tests
def test_set_cap_leverage(factory, market, gov):
    pass


def test_set_cap_leverage_reverts_when_not_gov(factory, alice):
    pass


def test_set_cap_leverage_reverts_when_less_than_min(factory, alice):
    pass


def test_set_cap_leverage_reverts_when_greater_than_max(factory, alice):
    pass


# maintenanceMargin tests
def test_set_maintenance_margin(factory, market, gov):
    pass


def test_set_maintenance_margin_reverts_when_not_gov(factory, alice):
    pass


def test_set_maintenance_margin_reverts_when_less_than_min(factory, alice):
    pass


def test_set_maintenance_margin_reverts_when_greater_than_max(factory, alice):
    pass


# maintenanceMarginBurnRate tests
def test_set_maintenance_margin_burn(factory, market, gov):
    pass


def test_set_maintenance_margin_burn_reverts_when_not_gov(factory, alice):
    pass


def test_set_maintenance_margin_burn_reverts_when_less_than_min(factory,
                                                                alice):
    pass


def test_set_maintenance_margin_burn_reverts_when_greater_than_max(factory,
                                                                   alice):
    pass


# tradingFeeRate tests
def test_set_trading_fee_rate(factory, market, gov):
    pass


def test_set_trading_fee_rate_reverts_when_not_gov(factory, alice):
    pass


def test_set_trading_fee_rate_reverts_when_less_than_min(factory, alice):
    pass


def test_set_trading_fee_rate_reverts_when_greater_than_max(factory, alice):
    pass


# minCollateral tests
def test_set_min_collateral_rate(factory, market, gov):
    pass


def test_set_min_collateral_reverts_when_not_gov(factory, alice):
    pass


def test_set_min_collateral_reverts_when_less_than_min(factory, alice):
    pass


def test_set_min_collateral_reverts_when_greater_than_max(factory, alice):
    pass
