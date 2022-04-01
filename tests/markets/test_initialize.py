from brownie import reverts


def test_initialize_reverts_when_not_factory(market, rando):
    # risk params
    params = [
        2220000000000,  # expect_k
        500000000000000000,  # expect_lmbda
        5000000000000000,  # expect_delta
        7000000000000000000,  # expect_cap_payoff
        900000000000000000000000,  # expect_cap_notional
        4000000000000000000,  # expect_cap_leverage
        3592000,  # expect_circuit_breaker_window
        96670000000000000000000,  # expect_circuit_breaker_mint_target
        50000000000000000,  # expect_maintenance_margin_fraction
        200000000000000000,  # expect_maintenance_margin_burn_rate
        5000000000000000,  # expect_liquidation_fee_rate
        250000000000000,  # expect_trading_fee_rate
        500000000000000,  # expect_min_collateral
        50000000000000,  # expect_price_drift_upper_limit
        14,  # expect_average_block_time
    ]
    with reverts("OVLV1: !factory"):
        _ = market.initialize(params, {"from": rando})
