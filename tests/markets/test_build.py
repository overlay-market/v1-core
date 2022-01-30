import pytest
from pytest import approx
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from decimal import Decimal
from hexbytes import HexBytes


# NOTE: Tests passing with isolation fixture
# TODO: Fix tests to pass even without isolation fixture (?)
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def calculate_position_info(oi: Decimal,
                            leverage: Decimal,
                            trading_fee_rate: Decimal) -> (Decimal, Decimal,
                                                           Decimal, Decimal):
    """
    Returns position attributes in decimal format (int / 1e18)
    """
    collateral = oi / leverage
    trade_fee = oi * trading_fee_rate
    debt = oi - collateral
    return collateral, oi, debt, trade_fee


def get_position_key(owner: str, id: int) -> HexBytes:
    """
    Returns the position key to retrieve an individual position
    from positions mapping
    """
    return web3.solidityKeccak(['address', 'uint256'], [owner, id])


@given(
    oi=strategy('decimal', min_value='0.001', max_value='800000', places=3),
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_creates_position(market, feed, ovl, alice, oi, leverage,
                                is_long):
    # get position key/id related info
    expect_pos_id = market.nextPositionId()

    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # input values for tx
    input_collateral = int((collateral) * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})

    # check position id
    actual_pos_id = tx.return_value
    assert actual_pos_id == expect_pos_id

    expect_next_pos_id = expect_pos_id + 1
    actual_next_pos_id = market.nextPositionId()
    assert actual_next_pos_id == expect_next_pos_id

    # calculate expected entry price
    # NOTE: ask(), bid() tested in test_price.py
    data = feed.latest()
    cap_oi = Decimal(market.capOi() / 1e18)
    volume = int((oi / cap_oi) * Decimal(1e18))
    price = market.ask(data, volume) if is_long \
        else market.bid(data, volume)

    # expect values
    expect_leverage = int(leverage * Decimal(1e18))
    expect_is_long = is_long
    expect_entry_price = price
    expect_oi_shares = int(oi * Decimal(1e18))
    expect_debt = int(debt * Decimal(1e18))
    expect_cost = int(collateral * Decimal(1e18))

    # check position info
    expect_pos_key = get_position_key(alice.address, expect_pos_id)
    actual_pos = market.positions(expect_pos_key)
    (actual_leverage, actual_is_long, actual_entry_price, actual_oi_shares,
     actual_debt, actual_cost) = actual_pos

    assert actual_leverage == expect_leverage
    assert actual_is_long == expect_is_long
    assert int(actual_entry_price) == approx(expect_entry_price)
    assert int(actual_oi_shares) == approx(expect_oi_shares)
    assert int(actual_debt) == approx(expect_debt)
    assert int(actual_cost) == approx(expect_cost)


@given(
    oi=strategy('decimal', min_value='0.001', max_value='800000', places=3),
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_adds_oi(market, ovl, alice, oi, leverage, is_long):
    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # input values for tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # priors actual values
    _ = market.update({"from": alice})  # update funding prior
    expect_oi = market.oiLong() if is_long else market.oiShort()
    expect_oi_shares = market.oiLongShares() \
        if is_long else market.oiShortShares()

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    # calculate expected oi info data
    expect_oi += int(oi * Decimal(1e18))
    expect_oi_shares += int(oi * Decimal(1e18))

    # compare with actual aggregate oi values
    actual_oi = market.oiLong() if is_long else market.oiShort()
    actual_oi_shares = market.oiLongShares() if is_long else market.oiShort()

    assert int(actual_oi) == approx(expect_oi)
    assert int(actual_oi_shares) == approx(expect_oi_shares)


@given(
    oi=strategy('decimal', min_value='0.001', max_value='800000', places=3),
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_registers_volume(market, feed, ovl, alice, oi, leverage,
                                is_long):
    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # input values for the tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # priors actual values
    _ = market.update({"from": alice})  # update funding prior
    snapshot_volume = market.snapshotVolumeAsk() if is_long else \
        market.snapshotVolumeBid()
    last_timestamp, last_window, last_volume = snapshot_volume

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})

    # calculate expected rolling volume and window numbers when
    # adjusted for decay
    # NOTE: decayOverWindow() tested in test_rollers.py
    _, micro_window, _, _, _, _, _, _, _, _ = feed.latest()
    cap_oi = Decimal(market.capOi() / 1e18)
    input_volume = int((oi / cap_oi) * Decimal(1e18))
    input_window = micro_window
    input_timestamp = chain[tx.block_number]['timestamp']

    # expect accumulator now to be calculated as
    # accumulatorLast * (1 - dt/windowLast) + value
    dt = input_timestamp - last_timestamp
    last_volume_decayed = last_volume * (1 - dt/last_window) \
        if last_window != 0 and dt >= last_window else 0
    expect_volume = int(last_volume_decayed + input_volume)

    # expect window now to be calculated as weighted average
    # of remaining time left in last window and total time in new window
    # weights are accumulator values for the respective time window
    numerator = int((last_window - dt) * last_volume_decayed
                    + input_window * input_volume)
    expect_window = int(numerator / expect_volume)
    expect_timestamp = input_timestamp

    # compare with actual rolling volume, timestamp last, window last values
    actual = market.snapshotVolumeAsk() if is_long else \
        market.snapshotVolumeBid()

    actual_timestamp, actual_window, actual_volume = actual

    assert actual_timestamp == expect_timestamp
    assert int(actual_window) == approx(expect_window)
    assert int(actual_volume) == approx(expect_volume)


@given(
    oi=strategy('decimal', min_value='0.001', max_value='800000', places=3),
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_executes_transfers(market, ovl, alice, oi, leverage,
                                  is_long):
    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # input values for the tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    # amount of collateral that will be transferred in
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    tx = market.build(input_collateral, input_leverage, input_is_long,
                      {"from": alice})

    # expected values
    expect_collateral_in = approve_collateral
    expect_trade_fee = int(trade_fee * Decimal(1e18))

    # check Transfer events for:
    # 1. collateral in; 2. trade fees out
    assert 'Transfer' in tx.events
    assert len(tx.events['Transfer']) == 2

    # check collateral in event (1)
    assert tx.events['Transfer'][0]['from'] == alice.address
    assert tx.events['Transfer'][0]['to'] == market.address
    assert int(tx.events['Transfer'][0]['value']) == \
        approx(expect_collateral_in)

    # check trade fee out event (2)
    assert tx.events['Transfer'][1]['from'] == market.address
    assert tx.events['Transfer'][1]['to'] == market.tradingFeeRecipient()
    assert int(tx.events['Transfer'][1]['value']) == approx(expect_trade_fee)


@given(
    oi=strategy('decimal', min_value='0.001', max_value='800000', places=3),
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_transfers_collateral_to_market(market, ovl, alice, oi,
                                              leverage, is_long):
    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # input values for the tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    # amount of collateral that will be transferred in
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # priors actual values
    expect_balance_alice = ovl.balanceOf(alice)
    expect_balance_market = ovl.balanceOf(market)

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    # calculate expected collateral info data
    expect_collateral_in = int((collateral + trade_fee) * Decimal(1e18))
    expect_balance_alice -= expect_collateral_in
    expect_balance_market += int(collateral * Decimal(1e18))

    actual_balance_alice = ovl.balanceOf(alice)
    actual_balance_market = ovl.balanceOf(market)

    assert int(actual_balance_alice) == approx(expect_balance_alice)
    assert int(actual_balance_market) == approx(expect_balance_market)


@given(
    oi=strategy('decimal', min_value='0.001', max_value='800000', places=3),
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_transfers_trading_fees(market, ovl, alice, oi,
                                      leverage, is_long):
    # calculate expected pos info data
    trading_fee_rate = Decimal(market.tradingFeeRate() / 1e18)
    collateral, oi, debt, trade_fee \
        = calculate_position_info(oi, leverage, trading_fee_rate)

    # input values for the tx
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long

    # approve collateral amount: collateral + trade fee
    # amount of collateral that will be transferred in
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # priors actual values
    recipient = market.tradingFeeRecipient()
    expect = ovl.balanceOf(recipient)

    # approve market for spending then build
    ovl.approve(market, approve_collateral, {"from": alice})
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    expect += int(trade_fee * Decimal(1e18))
    actual = ovl.balanceOf(recipient)

    assert int(actual) == approx(expect)


def test_build_reverts_when_leverage_less_than_one(market, ovl, alice):
    # get position key/id related info
    expect_pos_id = market.nextPositionId()

    input_collateral = int(100 * Decimal(1e18))
    input_is_long = True

    # approve market for spending before build
    ovl.approve(market, 2**256-1, {"from": alice})

    # check build reverts when input leverage is less than one (ONE = 1e18)
    input_leverage = int(Decimal(1e18) - 1)
    with reverts("OVLV1:lev<min"):
        _ = market.build(input_collateral, input_leverage, input_is_long,
                         {"from": alice})

    # check build succeeds when input leverage is equal to one
    input_leverage = int(Decimal(1e18))
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    # check position info
    expect_pos_key = get_position_key(alice.address, expect_pos_id)
    actual_pos = market.positions(expect_pos_key)

    expect_leverage = input_leverage
    (actual_leverage, _, _, _, _, _) = actual_pos
    assert actual_leverage == expect_leverage


def test_build_reverts_when_leverage_greater_than_cap(market, ovl, alice):
    # get position key/id related info
    expect_pos_id = market.nextPositionId()

    input_collateral = int(100 * Decimal(1e18))
    input_is_long = True

    # approve market for spending before build. Use the max just for here
    ovl.approve(market, 2**256 - 1, {"from": alice})

    # check build reverts when input leverage is less than one (ONE = 1e18)
    input_leverage = market.capLeverage() + 1
    with reverts("OVLV1:lev>max"):
        _ = market.build(input_collateral, input_leverage, input_is_long,
                         {"from": alice})

    # check build succeeds when input leverage is equal to cap
    input_leverage = market.capLeverage()
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    # check position info
    expect_pos_key = get_position_key(alice.address, expect_pos_id)
    actual_pos = market.positions(expect_pos_key)

    expect_leverage = input_leverage
    (actual_leverage, _, _, _, _, _) = actual_pos
    assert actual_leverage == expect_leverage


# TODO: def test_build_reverts_when_slippage_greater_than_max:


@given(
    leverage=strategy('decimal', min_value='1.0', max_value='5.0', places=3),
    is_long=strategy('bool'))
def test_build_reverts_when_collateral_less_than_min(market, ovl, alice,
                                                     leverage, is_long):
    # get position key/id related info
    expect_pos_id = market.nextPositionId()

    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = is_long
    input_collateral = market.minCollateral() - 1

    # approve market for spending then build. use max
    ovl.approve(market, 2**256 - 1, {"from": alice})

    # check build reverts for min_collat > collat
    with reverts("OVLV1:collateral<min"):
        _ = market.build(input_collateral, input_leverage, input_is_long,
                         {"from": alice})

    # check build succeeds for min_collat <= collat
    input_collateral = market.minCollateral()
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    expect_pos_id += 1
    actual_pos_id = market.nextPositionId()

    assert expect_pos_id == actual_pos_id


# TODO: fix this for cap adjustments
@given(is_long=strategy('bool'))
def test_build_reverts_when_oi_greater_than_cap(market, ovl, alice, is_long):
    # get position key/id related info
    expect_pos_id = market.nextPositionId()

    input_leverage = int(1e18)
    input_is_long = is_long

    # approve market for spending before build. use max
    ovl.approve(market, 2**256 - 1, {"from": alice})

    # check build reverts when oi is greater than static cap
    input_collateral = market.capOi() + 1
    with reverts("OVLV1:oi>cap"):
        _ = market.build(input_collateral, input_leverage, input_is_long,
                         {"from": alice})

    # check build succeeds when oi is equal to cap
    input_collateral = market.capOi()
    _ = market.build(input_collateral, input_leverage, input_is_long,
                     {"from": alice})

    # calculate expected pos info data
    leverage = 1
    oi = int(Decimal(input_collateral * leverage) / Decimal(1e18))
    collateral = int(Decimal(input_collateral) / Decimal(1e18))

    # expect values
    expect_oi_shares = int(oi * Decimal(1e18))
    expect_cost = int(collateral * Decimal(1e18))

    # check position info
    expect_pos_key = get_position_key(alice.address, expect_pos_id)
    actual_pos = market.positions(expect_pos_key)
    (_, _, _, actual_oi_shares, _, actual_cost) = actual_pos

    assert int(actual_oi_shares) == approx(expect_oi_shares)
    assert int(actual_cost) == approx(expect_cost)
