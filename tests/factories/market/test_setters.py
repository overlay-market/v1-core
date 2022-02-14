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


# circuitBreakerWindow tests
def test_set_circuit_breaker_window(factory, market, gov):
    feed = market.feed()
    expect_circuit_breaker_window = 172800

    # set circuitBreakerWindow
    tx = factory.setCircuitBreakerWindow(feed, expect_circuit_breaker_window,
                                         {"from": gov})

    # check circuitBreakerWindow changed
    actual_circuit_breaker_window = market.circuitBreakerWindow()
    assert expect_circuit_breaker_window == actual_circuit_breaker_window

    # check event emitted
    assert 'CircuitBreakerWindowUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "circuitBreakerWindow": expect_circuit_breaker_window
    })
    actual_event = tx.events['CircuitBreakerWindowUpdated']
    assert actual_event == expect_event


def test_set_circuit_breaker_window_reverts_when_not_gov(factory, market,
                                                         alice):
    feed = market.feed()
    expect_circuit_breaker_window = 172800

    # check can't set circuitBreakerWindow with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setCircuitBreakerWindow(feed,
                                            expect_circuit_breaker_window,
                                            {"from": alice})


def test_set_circuit_breaker_window_reverts_when_less_than_min(factory, market,
                                                               gov):
    feed = market.feed()
    expect_circuit_breaker_window = factory.MIN_CIRCUIT_BREAKER_WINDOW() - 1

    # check can't set circuitBreakerWindow less than min
    with reverts("OVLV1: circuitBreakerWindow out of bounds"):
        _ = factory.setCircuitBreakerWindow(feed,
                                            expect_circuit_breaker_window,
                                            {"from": gov})

    # check can set circuitBreakerWindow when equal to min
    expect_circuit_breaker_window = factory.MIN_CIRCUIT_BREAKER_WINDOW()
    factory.setCircuitBreakerWindow(feed, expect_circuit_breaker_window,
                                    {"from": gov})

    actual_circuit_breaker_window = market.circuitBreakerWindow()
    assert actual_circuit_breaker_window == expect_circuit_breaker_window


def test_set_circuit_breaker_window_reverts_when_greater_than_max(factory,
                                                                  market,
                                                                  gov):
    feed = market.feed()
    expect_circuit_breaker_window = factory.MAX_CIRCUIT_BREAKER_WINDOW() + 1

    # check can't set circuitBreakerWindow greater than max
    with reverts("OVLV1: circuitBreakerWindow out of bounds"):
        _ = factory.setCircuitBreakerWindow(feed,
                                            expect_circuit_breaker_window,
                                            {"from": gov})

    # check can set circuitBreakerWindow when equal to max
    expect_circuit_breaker_window = factory.MAX_CIRCUIT_BREAKER_WINDOW()
    factory.setCircuitBreakerWindow(feed, expect_circuit_breaker_window,
                                    {"from": gov})

    actual_circuit_breaker_window = market.circuitBreakerWindow()
    assert actual_circuit_breaker_window == expect_circuit_breaker_window


# circuitBreakerMintTarget tests
def test_set_circuit_breaker_mint_target(factory, market, gov):
    feed = market.feed()
    expect_circuit_breaker_mint_target = 100000000000000000000000

    # set circuitBreakerMintTarget
    tx = factory.setCircuitBreakerMintTarget(
        feed, expect_circuit_breaker_mint_target, {"from": gov})

    # check circuitBreakerMintTarget changed
    actual_circuit_breaker_mint_target = market.circuitBreakerMintTarget()
    assert expect_circuit_breaker_mint_target == \
        actual_circuit_breaker_mint_target

    # check event emitted
    assert 'CircuitBreakerMintTargetUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "circuitBreakerMintTarget": expect_circuit_breaker_mint_target
    })
    actual_event = tx.events['CircuitBreakerMintTargetUpdated']
    assert actual_event == expect_event


def test_set_circuit_breaker_target_reverts_when_not_gov(factory, market,
                                                         alice):
    feed = market.feed()
    expect_circuit_breaker_mint_target = 100000000000000000000000

    # check can't set circuitBreakerMintTarget with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setCircuitBreakerMintTarget(
            feed, expect_circuit_breaker_mint_target, {"from": alice})


def test_set_circuit_breaker_target_reverts_when_greater_than_max(factory,
                                                                  market,
                                                                  gov):
    feed = market.feed()
    expect_circuit_breaker_mint_target = \
        factory.MAX_CIRCUIT_BREAKER_MINT_TARGET() + 1

    # check can't set circuitBreakerMintTarget greater than max
    with reverts("OVLV1: circuitBreakerMintTarget out of bounds"):
        _ = factory.setCircuitBreakerMintTarget(
            feed, expect_circuit_breaker_mint_target, {"from": gov})

    # check can set circuitBreakerMintTarget when equal to max
    expect_circuit_breaker_mint_target = \
        factory.MAX_CIRCUIT_BREAKER_MINT_TARGET()
    factory.setCircuitBreakerMintTarget(
        feed, expect_circuit_breaker_mint_target, {"from": gov})

    actual_circuit_breaker_mint_target = market.circuitBreakerMintTarget()
    assert actual_circuit_breaker_mint_target == \
        expect_circuit_breaker_mint_target


# maintenanceMarginFraction tests
def test_set_maintenance_margin(factory, market, gov):
    feed = market.feed()
    expect_maintenance_margin = 75000000000000000

    # set maintenanceMarginFraction
    tx = factory.setMaintenanceMarginFraction(feed, expect_maintenance_margin,
                                              {"from": gov})

    # check maintenanceMarginFraction changed
    actual_maintenance_margin = market.maintenanceMarginFraction()
    assert expect_maintenance_margin == actual_maintenance_margin

    # check event emitted
    assert 'MaintenanceMarginFractionUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "maintenanceMarginFraction": expect_maintenance_margin
    })
    actual_event = tx.events['MaintenanceMarginFractionUpdated']
    assert actual_event == expect_event


def test_set_maintenance_margin_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_maintenance_margin = 75000000000000000

    # check can't set maintenanceMarginFraction with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setMaintenanceMarginFraction(feed,
                                                 expect_maintenance_margin,
                                                 {"from": alice})


def test_set_maintenance_margin_reverts_when_less_than_min(factory, market,
                                                           gov):
    feed = market.feed()
    expect_maintenance_margin = factory.MIN_MAINTENANCE_MARGIN_FRACTION() - 1

    # check can't set maintenanceMarginFraction less than min
    with reverts("OVLV1: maintenanceMarginFraction out of bounds"):
        _ = factory.setMaintenanceMarginFraction(feed,
                                                 expect_maintenance_margin,
                                                 {"from": gov})

    # check can set maintenanceMargin when equal to min
    expect_maintenance_margin = factory.MIN_MAINTENANCE_MARGIN_FRACTION()
    factory.setMaintenanceMarginFraction(feed, expect_maintenance_margin,
                                         {"from": gov})

    actual_maintenance_margin = market.maintenanceMarginFraction()
    assert actual_maintenance_margin == expect_maintenance_margin


def test_set_maintenance_margin_reverts_when_greater_than_max(factory, market,
                                                              gov):
    feed = market.feed()
    expect_maintenance_margin = factory.MAX_MAINTENANCE_MARGIN_FRACTION() + 1

    # check can't set maintenanceMarginFraction greater than max
    with reverts("OVLV1: maintenanceMarginFraction out of bounds"):
        _ = factory.setMaintenanceMarginFraction(feed,
                                                 expect_maintenance_margin,
                                                 {"from": gov})

    # check can set maintenanceMargin when equal to max
    expect_maintenance_margin = factory.MAX_MAINTENANCE_MARGIN_FRACTION()
    factory.setMaintenanceMarginFraction(feed, expect_maintenance_margin,
                                         {"from": gov})

    actual_maintenance_margin = market.maintenanceMarginFraction()
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


# liquidationFeeRate tests
def test_set_liquidation_fee_rate(factory, market, gov):
    feed = market.feed()
    expect_liquidation_fee_rate = 5000000000000000

    # set liquidationFeeRate
    tx = factory.setLiquidationFeeRate(feed, expect_liquidation_fee_rate,
                                       {"from": gov})

    # check liquidationFeeRate changed
    actual_liquidation_fee_rate = market.liquidationFeeRate()
    assert expect_liquidation_fee_rate == actual_liquidation_fee_rate

    # check event emitted
    assert 'LiquidationFeeRateUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "liquidationFeeRate": expect_liquidation_fee_rate
    })
    actual_event = tx.events['LiquidationFeeRateUpdated']
    assert actual_event == expect_event


def test_set_liquidation_fee_rate_reverts_when_not_gov(factory, market, alice):
    feed = market.feed()
    expect_liquidation_fee_rate = 5000000000000000

    # check can't set liquidationFeeRate with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setLiquidationFeeRate(feed, expect_liquidation_fee_rate,
                                          {"from": alice})


def test_set_liquidation_fee_rate_reverts_when_less_than_min(factory, market,
                                                             gov):
    feed = market.feed()
    expect_liquidation_fee_rate = factory.MIN_LIQUIDATION_FEE_RATE() - 1

    # check can't set liquidationFeeRate less than min
    with reverts("OVLV1: liquidationFeeRate out of bounds"):
        _ = factory.setLiquidationFeeRate(feed, expect_liquidation_fee_rate,
                                          {"from": gov})

    # check can set liquidationFeeRate when equal to min
    expect_liquidation_fee_rate = factory.MIN_LIQUIDATION_FEE_RATE()
    factory.setLiquidationFeeRate(feed, expect_liquidation_fee_rate,
                                  {"from": gov})

    actual_liquidation_fee_rate = market.liquidationFeeRate()
    assert actual_liquidation_fee_rate == expect_liquidation_fee_rate


def test_set_liquidation_fee_rate_reverts_when_greater_than_max(factory,
                                                                market,
                                                                gov):
    feed = market.feed()
    expect_liquidation_fee_rate = factory.MAX_LIQUIDATION_FEE_RATE() + 1

    # check can't set liquidationFeeRate greater than max
    with reverts("OVLV1: liquidationFeeRate out of bounds"):
        _ = factory.setLiquidationFeeRate(feed, expect_liquidation_fee_rate,
                                          {"from": gov})

    # check can set liquidationFeeRate when equal to max
    expect_liquidation_fee_rate = factory.MAX_LIQUIDATION_FEE_RATE()
    factory.setLiquidationFeeRate(feed, expect_liquidation_fee_rate,
                                  {"from": gov})

    actual_liquidation_fee_rate = market.liquidationFeeRate()
    assert actual_liquidation_fee_rate == expect_liquidation_fee_rate


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


# priceDriftUpperLimit tests
def test_set_price_drift_upper_limit(factory, market, gov):
    feed = market.feed()
    expect_price_drift_upper_limit = 700000000000000

    # set priceDriftUpperLimit
    tx = factory.setPriceDriftUpperLimit(feed, expect_price_drift_upper_limit,
                                         {"from": gov})

    # check priceDriftUpperLimit changed
    actual_price_drift_upper_limit = market.priceDriftUpperLimit()
    assert expect_price_drift_upper_limit == actual_price_drift_upper_limit

    # check event emitted
    assert 'PriceDriftUpperLimitUpdated' in tx.events
    expect_event = OrderedDict({
        "user": gov,
        "market": market,
        "priceDriftUpperLimit": expect_price_drift_upper_limit
    })
    actual_event = tx.events['PriceDriftUpperLimitUpdated']
    assert actual_event == expect_event


def test_set_price_drift_upper_limit_reverts_when_not_gov(factory, market,
                                                          alice):
    feed = market.feed()
    expect_price_drift_upper_limit = 700000000000000

    # check can't set priceDriftUpperLimit with non gov account
    with reverts("OVLV1: !governor"):
        _ = factory.setPriceDriftUpperLimit(
            feed, expect_price_drift_upper_limit, {"from": alice})


def test_set_price_drift_upper_limit_reverts_when_less_than_min(factory,
                                                                market, gov):
    feed = market.feed()
    expect_price_drift_upper_limit = factory.MIN_PRICE_DRIFT_UPPER_LIMIT() - 1

    # check can't set priceDriftUpperLimit less than min
    with reverts("OVLV1: priceDriftUpperLimit out of bounds"):
        _ = factory.setPriceDriftUpperLimit(
            feed, expect_price_drift_upper_limit, {"from": gov})

    # check can set priceDriftUpperLimit when equal to min
    expect_price_drift_upper_limit = factory.MIN_PRICE_DRIFT_UPPER_LIMIT()
    factory.setPriceDriftUpperLimit(feed, expect_price_drift_upper_limit,
                                    {"from": gov})

    actual_price_drift_upper_limit = market.priceDriftUpperLimit()
    assert actual_price_drift_upper_limit == expect_price_drift_upper_limit


def test_set_price_drift_upper_limit_reverts_when_greater_than_max(factory,
                                                                   market,
                                                                   gov):
    feed = market.feed()
    expect_price_drift_upper_limit = factory.MAX_PRICE_DRIFT_UPPER_LIMIT() + 1

    # check can't set priceDriftUpperLimit greater than max
    with reverts("OVLV1: priceDriftUpperLimit out of bounds"):
        _ = factory.setPriceDriftUpperLimit(feed,
                                            expect_price_drift_upper_limit,
                                            {"from": gov})

    # check can set priceDriftUpperLimit when equal to max
    expect_price_drift_upper_limit = factory.MAX_PRICE_DRIFT_UPPER_LIMIT()
    factory.setPriceDriftUpperLimit(feed, expect_price_drift_upper_limit,
                                    {"from": gov})

    actual_price_drift_upper_limit = market.priceDriftUpperLimit()
    assert actual_price_drift_upper_limit == expect_price_drift_upper_limit
