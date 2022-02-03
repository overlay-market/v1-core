from brownie import chain
from decimal import Decimal


def test_multiple_unwind_unwinds_multiple_positions(market, alice, ovl):
    # get position key/id related info
    # expect_pos_id = market.nextPositionId()

    # loop through 10 times
    n = 10
    collateral = Decimal(1000)
    leverage = Decimal(1.0)
    is_long = True

    # input collateral for each build tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)

    # total approve collateral
    approve_collateral = n * input_collateral * (1 + trading_fee_rate)
    ovl.approve(market, approve_collateral, {"from": alice})

    actual_pos_ids = []
    for i in range(n):
        tx = market.build(input_collateral, input_leverage, input_is_long,
                          {"from": alice})
        pos_id = tx.return_value
        actual_pos_ids.append(pos_id)

    # mine the chain into the future then unwind each
    chain.mine(timedelta=600)

    # unwind all of each position
    for id in actual_pos_ids:
        tx = market.unwind(id, 1e18, {"from": alice})
