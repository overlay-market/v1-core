from brownie import reverts
from collections import OrderedDict


# k tests
def test_set_k(factory, market, gov):
    feed = market.feed()
    expect_k = 361250000000

    # set k
    tx = factory.setK(feed, expect_k, {"from": gov})

    # check k changed
    actual_k = market.k()
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


def test_set_k_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_k = 361250000000

    # check can't set k with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setK(feed, expect_k, {"from": alice})


def test_set_k_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()
    expect_k = factory.MIN_K() - 1

    # check can't set k less than min
    with reverts("OVLV1: k out of bounds"):
        _ = factory.setK(feed, expect_k, {"from": gov})

    # check can set k when equal to min
    expect_k = factory.MIN_K()
    factory.setK(feed, expect_k, {"from": gov})

    actual_k = market.k()
    assert actual_k == expect_k


def test_set_k_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()
    expect_k = factory.MAX_K() + 1

    # check can't set k greater than max
    with reverts("OVLV1: k out of bounds"):
        _ = factory.setK(feed, expect_k, {"from": gov})

    # check can set k when equal to max
    expect_k = factory.MAX_K()
    factory.setK(feed, expect_k, {"from": gov})

    actual_k = market.k()
    assert actual_k == expect_k


# lmbda tests
def test_set_lmbda(factory, market, gov):
    feed = market.feed()
    expect_lmbda = 5000000000000000000

    # set lmbda
    tx = factory.setLmbda(feed, expect_lmbda, {"from": gov})

    # check lmbda changed
    actual_lmbda = market.lmbda()
    assert expect_lmbda == actual_lmbda

    # check event emitted
    assert 'ImpactUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "lmbda": expect_lmbda
    })
    actual_event = tx.events['ImpactUpdated']
    assert actual_event == expect_event


def test_set_lmbda_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_lmbda = 5000000000000000000

    # check can't set lmbda with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setLmbda(feed, expect_lmbda, {"from": alice})


def test_set_lmbda_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()
    expect_lmbda = factory.MIN_LMBDA() - 1

    # check can't set lmbda less than min
    with reverts("OVLV1: lmbda out of bounds"):
        _ = factory.setLmbda(feed, expect_lmbda, {"from": gov})

    # check can set lmbda when equal to min
    expect_lmbda = factory.MIN_LMBDA()
    factory.setLmbda(feed, expect_lmbda, {"from": gov})

    actual_lmbda = market.lmbda()
    assert actual_lmbda == expect_lmbda


def test_set_lmbda_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()
    expect_lmbda = factory.MAX_LMBDA() + 1

    # check can't set lmbda greater than max
    with reverts("OVLV1: lmbda out of bounds"):
        _ = factory.setLmbda(feed, expect_lmbda, {"from": gov})

    # check can set lmbda when equal to max
    expect_lmbda = factory.MAX_LMBDA()
    factory.setLmbda(feed, expect_lmbda, {"from": gov})

    actual_lmbda = market.lmbda()
    assert actual_lmbda == expect_lmbda


# delta tests
def test_set_delta(factory, market, gov):
    feed = market.feed()
    expect_delta = 1000000000000000

    # set delta
    tx = factory.setDelta(feed, expect_delta, {"from": gov})

    # check delta changed
    actual_delta = market.delta()
    assert expect_delta == actual_delta

    # check event emitted
    assert 'SpreadUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "delta": expect_delta
    })
    actual_event = tx.events['SpreadUpdated']
    assert actual_event == expect_event


def test_set_delta_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_delta = 1000000000000000

    # check can't set delta with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setDelta(feed, expect_delta, {"from": alice})


def test_set_delta_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()
    expect_delta = factory.MIN_DELTA() - 1

    # check can't set delta less than min
    with reverts("OVLV1: delta out of bounds"):
        _ = factory.setDelta(feed, expect_delta, {"from": gov})

    # check can set delta when equal to min
    expect_delta = factory.MIN_DELTA()
    factory.setDelta(feed, expect_delta, {"from": gov})

    actual_delta = market.delta()
    assert actual_delta == expect_delta


def test_set_delta_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()
    expect_delta = factory.MAX_DELTA() + 1

    # check can't set delta greater than max
    with reverts("OVLV1: delta out of bounds"):
        _ = factory.setDelta(feed, expect_delta, {"from": gov})

    # check can set delta when equal to max
    expect_delta = factory.MAX_DELTA()
    factory.setDelta(feed, expect_delta, {"from": gov})

    actual_delta = market.delta()
    assert actual_delta == expect_delta


# capPayoff tests
def test_set_cap_payoff(factory, market, gov):
    feed = market.feed()
    expect_cap_payoff = 7000000000000000000

    # set capPayoff
    tx = factory.setCapPayoff(feed, expect_cap_payoff, {"from": gov})

    # check capPayoff changed
    actual_cap_payoff = market.capPayoff()
    assert expect_cap_payoff == actual_cap_payoff

    # check event emitted
    assert 'PayoffCapUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "capPayoff": expect_cap_payoff
    })
    actual_event = tx.events['PayoffCapUpdated']
    assert actual_event == expect_event


def test_set_cap_payoff_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_cap_payoff = 7000000000000000000

    # check can't set capPayoff with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setCapPayoff(feed, expect_cap_payoff, {"from": alice})


def test_set_cap_payoff_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()
    expect_cap_payoff = factory.MIN_CAP_PAYOFF() - 1

    # check can't set capPayoff less than min
    with reverts("OVLV1: capPayoff out of bounds"):
        _ = factory.setCapPayoff(feed, expect_cap_payoff, {"from": gov})

    # check can set capPayoff when equal to min
    expect_cap_payoff = factory.MIN_CAP_PAYOFF()
    factory.setCapPayoff(feed, expect_cap_payoff, {"from": gov})

    actual_cap_payoff = market.capPayoff()
    assert actual_cap_payoff == expect_cap_payoff


def test_set_cap_payoff_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()
    expect_cap_payoff = factory.MAX_CAP_PAYOFF() + 1

    # check can't set capPayoff greater than max
    with reverts("OVLV1: capPayoff out of bounds"):
        _ = factory.setCapPayoff(feed, expect_cap_payoff, {"from": gov})

    # check can set capPayoff when equal to max
    expect_cap_payoff = factory.MAX_CAP_PAYOFF()
    factory.setCapPayoff(feed, expect_cap_payoff, {"from": gov})

    actual_cap_payoff = market.capPayoff()
    assert actual_cap_payoff == expect_cap_payoff


# capOi tests
def test_set_cap_oi(factory, market, gov):
    feed = market.feed()
    expect_cap_oi = 700000000000000000000

    # set capOi
    tx = factory.setCapOi(feed, expect_cap_oi, {"from": gov})

    # check capOi changed
    actual_cap_oi = market.capOi()
    assert expect_cap_oi == actual_cap_oi

    # check event emitted
    assert 'OpenInterestCapUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "capOi": expect_cap_oi
    })
    actual_event = tx.events['OpenInterestCapUpdated']
    assert actual_event == expect_event


def test_set_cap_oi_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_cap_oi = 700000000000000000000

    # check can't set capOi with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setCapOi(feed, expect_cap_oi, {"from": alice})


# NOTE: don't have test_set_cap_oi_reverts_when_less_than_min because
# MIN_CAP_OI is zero


def test_set_cap_oi_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()
    expect_cap_oi = factory.MAX_CAP_OI() + 1

    # check can't set capOi greater than max
    with reverts("OVLV1: capOi out of bounds"):
        _ = factory.setCapOi(feed, expect_cap_oi, {"from": gov})

    # check can set capOi when equal to max
    expect_cap_oi = factory.MAX_CAP_OI()
    factory.setCapOi(feed, expect_cap_oi, {"from": gov})

    actual_cap_oi = market.capOi()
    assert actual_cap_oi == expect_cap_oi


# capLeverage tests
def test_set_cap_leverage(factory, market, gov):
    feed = market.feed()
    expect_cap_leverage = 7000000000000000000

    # set capLeverage
    tx = factory.setCapLeverage(feed, expect_cap_leverage, {"from": gov})

    # check capLeverage changed
    actual_cap_leverage = market.capLeverage()
    assert expect_cap_leverage == actual_cap_leverage

    # check event emitted
    assert 'LeverageCapUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "capLeverage": expect_cap_leverage
    })
    actual_event = tx.events['LeverageCapUpdated']
    assert actual_event == expect_event


def test_set_cap_leverage_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_cap_leverage = 7000000000000000000

    # check can't set capLeverage with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setCapLeverage(feed, expect_cap_leverage, {"from": alice})


def test_set_cap_leverage_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()
    expect_cap_leverage = factory.MIN_CAP_LEVERAGE() - 1

    # check can't set capLeverage less than min
    with reverts("OVLV1: capLeverage out of bounds"):
        _ = factory.setCapLeverage(feed, expect_cap_leverage, {"from": gov})

    # check can set capLeverage when equal to min
    expect_cap_leverage = factory.MIN_CAP_LEVERAGE()
    factory.setCapLeverage(feed, expect_cap_leverage, {"from": gov})

    actual_cap_leverage = market.capLeverage()
    assert actual_cap_leverage == expect_cap_leverage


def test_set_cap_leverage_reverts_when_greater_than_max(factory, market, gov):
    feed = market.feed()
    expect_cap_leverage = factory.MAX_CAP_LEVERAGE() + 1

    # check can't set capLeverage greater than max
    with reverts("OVLV1: capLeverage out of bounds"):
        _ = factory.setCapLeverage(feed, expect_cap_leverage, {"from": gov})

    # check can set capLeverage when equal to max
    expect_cap_leverage = factory.MAX_CAP_LEVERAGE()
    factory.setCapLeverage(feed, expect_cap_leverage, {"from": gov})

    actual_cap_leverage = market.capLeverage()
    assert actual_cap_leverage == expect_cap_leverage


# maintenanceMargin tests
def test_set_maintenance_margin(factory, market, gov):
    feed = market.feed()
    expect_maintenance_margin = 75000000000000000

    # set maintenanceMargin
    tx = factory.setMaintenanceMargin(feed, expect_maintenance_margin,
                                      {"from": gov})

    # check maintenanceMargin changed
    actual_maintenance_margin = market.maintenanceMargin()
    assert expect_maintenance_margin == actual_maintenance_margin

    # check event emitted
    assert 'MaintenanceMarginUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "maintenanceMargin": expect_maintenance_margin
    })
    actual_event = tx.events['MaintenanceMarginUpdated']
    assert actual_event == expect_event


def test_set_maintenance_margin_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_maintenance_margin = 75000000000000000

    # check can't set maintenanceMargin with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setMaintenanceMargin(feed, expect_maintenance_margin,
                                         {"from": alice})


def test_set_maintenance_margin_reverts_when_less_than_min(factory, market,
                                                           gov):
    feed = market.feed()
    expect_maintenance_margin = factory.MIN_MAINTENANCE_MARGIN() - 1

    # check can't set maintenanceMargin less than min
    with reverts("OVLV1: maintenanceMargin out of bounds"):
        _ = factory.setMaintenanceMargin(feed, expect_maintenance_margin,
                                         {"from": gov})

    # check can set maintenanceMargin when equal to min
    expect_maintenance_margin = factory.MIN_MAINTENANCE_MARGIN()
    factory.setMaintenanceMargin(feed, expect_maintenance_margin,
                                 {"from": gov})

    actual_maintenance_margin = market.maintenanceMargin()
    assert actual_maintenance_margin == expect_maintenance_margin


def test_set_maintenance_margin_reverts_when_greater_than_max(factory, market,
                                                              gov):
    feed = market.feed()
    expect_maintenance_margin = factory.MAX_MAINTENANCE_MARGIN() + 1

    # check can't set maintenanceMargin greater than max
    with reverts("OVLV1: maintenanceMargin out of bounds"):
        _ = factory.setMaintenanceMargin(feed, expect_maintenance_margin,
                                         {"from": gov})

    # check can set maintenanceMargin when equal to max
    expect_maintenance_margin = factory.MAX_MAINTENANCE_MARGIN()
    factory.setMaintenanceMargin(feed, expect_maintenance_margin,
                                 {"from": gov})

    actual_maintenance_margin = market.maintenanceMargin()
    assert actual_maintenance_margin == expect_maintenance_margin


# maintenanceMarginBurnRate tests
def test_set_maintenance_margin_burn(factory, market, gov):
    feed = market.feed()
    expect_maintenance_margin_burn = 75000000000000000

    # set maintenanceMarginBurnRate
    tx = factory.setMaintenanceMarginBurnRate(feed,
                                              expect_maintenance_margin_burn,
                                              {"from": gov})

    # check maintenanceMarginBurnRate changed
    actual_maintenance_margin_burn = market.maintenanceMarginBurnRate()
    assert expect_maintenance_margin_burn == actual_maintenance_margin_burn

    # check event emitted
    assert 'MaintenanceMarginBurnRateUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "maintenanceMarginBurnRate": expect_maintenance_margin_burn
    })
    actual_event = tx.events['MaintenanceMarginBurnRateUpdated']
    assert actual_event == expect_event


def test_set_maintenance_margin_burn_reverts_when_not_gov(factory, market,
                                                          alice):
    feed = market.feed()
    expect_maintenance_margin_burn = 75000000000000000

    # check can't set maintenanceMarginBurnRate with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setMaintenanceMarginBurnRate(
            feed, expect_maintenance_margin_burn, {"from": alice})


def test_set_maintenance_margin_burn_reverts_when_less_than_min(factory,
                                                                market,
                                                                gov):
    feed = market.feed()
    expect_margin_burn = factory.MIN_MAINTENANCE_MARGIN_BURN_RATE() - 1

    # check can't set maintenanceMarginBurnRate less than min
    with reverts("OVLV1: maintenanceMarginBurnRate out of bounds"):
        _ = factory.setMaintenanceMarginBurnRate(feed, expect_margin_burn,
                                                 {"from": gov})

    # check can set maintenanceMarginBurnRate when equal to min
    expect_margin_burn = factory.MIN_MAINTENANCE_MARGIN_BURN_RATE()
    factory.setMaintenanceMarginBurnRate(feed, expect_margin_burn,
                                         {"from": gov})

    actual_margin_burn = market.maintenanceMarginBurnRate()
    assert actual_margin_burn == expect_margin_burn


def test_set_maintenance_margin_burn_reverts_when_greater_than_max(factory,
                                                                   market,
                                                                   gov):
    feed = market.feed()
    expect_margin_burn = factory.MAX_MAINTENANCE_MARGIN_BURN_RATE() + 1

    # check can't set maintenanceMarginBurnRate greater than max
    with reverts("OVLV1: maintenanceMarginBurnRate out of bounds"):
        _ = factory.setMaintenanceMarginBurnRate(feed, expect_margin_burn,
                                                 {"from": gov})

    # check can set maintenanceMarginBurnRate when equal to max
    expect_margin_burn = factory.MAX_MAINTENANCE_MARGIN_BURN_RATE()
    factory.setMaintenanceMarginBurnRate(feed, expect_margin_burn,
                                         {"from": gov})

    actual_margin_burn = market.maintenanceMarginBurnRate()
    assert actual_margin_burn == expect_margin_burn


# tradingFeeRate tests
def test_set_trading_fee_rate(factory, market, gov):
    feed = market.feed()
    expect_trading_fee_rate = 1000000000000000

    # set tradingFeeRate
    tx = factory.setTradingFeeRate(feed, expect_trading_fee_rate,
                                   {"from": gov})

    # check tradingFeeRate changed
    actual_trading_fee_rate = market.tradingFeeRate()
    assert expect_trading_fee_rate == actual_trading_fee_rate

    # check event emitted
    assert 'TradingFeeRateUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "tradingFeeRate": expect_trading_fee_rate
    })
    actual_event = tx.events['TradingFeeRateUpdated']
    assert actual_event == expect_event


def test_set_trading_fee_rate_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_trading_fee_rate = 1000000000000000

    # check can't set tradingFeeRate with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setTradingFeeRate(feed, expect_trading_fee_rate,
                                      {"from": alice})


def test_set_trading_fee_rate_reverts_when_less_than_min(factory, market,
                                                         gov):
    feed = market.feed()
    expect_trading_fee_rate = factory.MIN_TRADING_FEE_RATE() - 1

    # check can't set tradingFeeRate less than min
    with reverts("OVLV1: tradingFeeRate out of bounds"):
        _ = factory.setTradingFeeRate(feed, expect_trading_fee_rate,
                                      {"from": gov})

    # check can set tradingFeeRate when equal to min
    expect_trading_fee_rate = factory.MIN_TRADING_FEE_RATE()
    factory.setTradingFeeRate(feed, expect_trading_fee_rate, {"from": gov})

    actual_trading_fee_rate = market.tradingFeeRate()
    assert actual_trading_fee_rate == expect_trading_fee_rate


def test_set_trading_fee_rate_reverts_when_greater_than_max(factory, market,
                                                            gov):
    feed = market.feed()
    expect_trading_fee_rate = factory.MAX_TRADING_FEE_RATE() + 1

    # check can't set tradingFeeRate greater than max
    with reverts("OVLV1: tradingFeeRate out of bounds"):
        _ = factory.setTradingFeeRate(feed, expect_trading_fee_rate,
                                      {"from": gov})

    # check can set tradingFeeRate when equal to max
    expect_trading_fee_rate = factory.MAX_TRADING_FEE_RATE()
    factory.setTradingFeeRate(feed, expect_trading_fee_rate, {"from": gov})

    actual_trading_fee_rate = market.tradingFeeRate()
    assert actual_trading_fee_rate == expect_trading_fee_rate


# minCollateral tests
def test_set_min_collateral(factory, market, gov):
    feed = market.feed()
    expect_min_collateral = 70000000000000

    # set minCollateral
    tx = factory.setMinCollateral(feed, expect_min_collateral,
                                  {"from": gov})

    # check minCollateral changed
    actual_min_collateral = market.minCollateral()
    assert expect_min_collateral == actual_min_collateral

    # check event emitted
    assert 'MinimumCollateralUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "minCollateral": expect_min_collateral
    })
    actual_event = tx.events['MinimumCollateralUpdated']
    assert actual_event == expect_event


def test_set_min_collateral_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_min_collateral = 70000000000000

    # check can't set minCollateral with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setMinCollateral(feed, expect_min_collateral,
                                     {"from": alice})


def test_set_min_collateral_reverts_when_less_than_min(factory, market, gov):
    feed = market.feed()
    expect_min_collateral = factory.MIN_MINIMUM_COLLATERAL() - 1

    # check can't set minCollateral less than min
    with reverts("OVLV1: minCollateral out of bounds"):
        _ = factory.setMinCollateral(feed, expect_min_collateral,
                                     {"from": gov})

    # check can set minCollateral when equal to min
    expect_min_collateral = factory.MIN_MINIMUM_COLLATERAL()
    factory.setMinCollateral(feed, expect_min_collateral, {"from": gov})

    actual_min_collateral = market.minCollateral()
    assert actual_min_collateral == expect_min_collateral


def test_set_min_collateral_reverts_when_greater_than_max(factory, market,
                                                          gov):
    feed = market.feed()
    expect_min_collateral = factory.MAX_MINIMUM_COLLATERAL() + 1

    # check can't set minCollateral greater than max
    with reverts("OVLV1: minCollateral out of bounds"):
        _ = factory.setMinCollateral(feed, expect_min_collateral,
                                     {"from": gov})

    # check can set minCollateral when equal to max
    expect_min_collateral = factory.MAX_MINIMUM_COLLATERAL()
    factory.setMinCollateral(feed, expect_min_collateral, {"from": gov})

    actual_min_collateral = market.minCollateral()
    assert actual_min_collateral == expect_min_collateral
