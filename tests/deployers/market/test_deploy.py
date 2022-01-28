from brownie import interface, reverts


def test_deploy_creates_market(deployer, ovl, feed, factory):
    # risk params
    k = 1220000000000
    lmbda = 1000000000000000000
    delta = 2500000000000000
    cap_payoff = 5000000000000000000
    cap_oi = 800000000000000000000000
    cap_leverage = 5000000000000000000
    circuit_breaker_window = 2592000
    circuit_breaker_mint_target = 66670000000000000000000
    maintenance_margin = 100000000000000000
    maintenance_margin_burn_rate = 100000000000000000
    trading_fee_rate = 750000000000000
    min_collateral = 100000000000000
    price_drift_upper_limit = 1000000000000000000

    params = (k, lmbda, delta, cap_payoff, cap_oi, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin, maintenance_margin_burn_rate,
              trading_fee_rate, min_collateral, price_drift_upper_limit)

    # deploy the market
    tx = deployer.deploy(ovl, feed, params, {"from": factory})
    market_addr = tx.return_value
    market = interface.IOverlayV1Market(market_addr)

    # check market deployed correctly with immutables
    assert market.ovl() == ovl
    assert market.feed() == feed
    assert market.factory() == factory
    assert market.tradingFeeRecipient() == factory

    # check market deployed correctly with risk params
    assert market.k() == k
    assert market.lmbda() == lmbda
    assert market.delta() == delta
    assert market.capPayoff() == cap_payoff
    assert market.capOi() == cap_oi
    assert market.capLeverage() == cap_leverage
    assert market.circuitBreakerWindow() == circuit_breaker_window
    assert market.circuitBreakerMintTarget() == circuit_breaker_mint_target
    assert market.maintenanceMargin() == maintenance_margin
    assert market.maintenanceMarginBurnRate() == maintenance_margin_burn_rate
    assert market.tradingFeeRate() == trading_fee_rate
    assert market.minCollateral() == min_collateral
    assert market.priceDriftUpperLimit() == price_drift_upper_limit


def test_deploy_reverts_when_not_factory(deployer, ovl, feed, rando):
    # risk params
    k = 1220000000000
    lmbda = 1000000000000000000
    delta = 2500000000000000
    cap_payoff = 5000000000000000000
    cap_oi = 800000000000000000000000
    cap_leverage = 5000000000000000000
    circuit_breaker_window = 2592000
    circuit_breaker_mint_target = 66670000000000000000000
    maintenance_margin = 100000000000000000
    maintenance_margin_burn_rate = 100000000000000000
    trading_fee_rate = 750000000000000
    min_collateral = 100000000000000
    price_drift_upper_limit = 1000000000000000000

    params = (k, lmbda, delta, cap_payoff, cap_oi, cap_leverage,
              circuit_breaker_window, circuit_breaker_mint_target,
              maintenance_margin, maintenance_margin_burn_rate,
              trading_fee_rate, min_collateral, price_drift_upper_limit)

    # check attempting to deploy
    with reverts("OVLV1: !factory"):
        deployer.deploy(ovl, feed, params, {"from": rando})
