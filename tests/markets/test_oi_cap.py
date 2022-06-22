from decimal import Decimal
from pytest import approx
from brownie.test import given, strategy

from .utils import calculate_position_info, mid_from_feed, RiskParameter


def test_cap_notional_front_run_bound(market, feed):
    idx = RiskParameter.LMBDA.value
    lmbda = Decimal(market.params(idx)) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    _, _, _, _, _, _, reserve_micro, _ = data

    # check front run bound is lmbda * reserveOverMicro when has reserve
    expect = int(lmbda * Decimal(reserve_micro))
    actual = market.frontRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_notional_back_run_bound(market, feed):
    idx = RiskParameter.DELTA.value
    delta = Decimal(market.params(idx)) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    average_block_time = market.params(RiskParameter.AVERAGE_BLOCK_TIME.value)
    _, _, macro_window, _, _, _, reserve_micro, _ = data

    # check back run bound is macroWindowInBlocks * reserveInOvl * 2 * delta
    # when has reserve
    window = Decimal(macro_window) / Decimal(average_block_time)
    expect = int(Decimal(2) * delta * Decimal(reserve_micro) * window)
    actual = market.backRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_notional_adjusted_for_bounds(market, feed):
    # Test cap notional adjustments is min of all bounds and circuit breaker
    idx = RiskParameter.CAP_NOTIONAL.value
    cap_notional = market.params(idx)
    data = feed.latest()

    # calculate cap notional bounds:
    # 1. front run bound; 2. back run bound
    cap_notional_front_run_bound = market.frontRunBound(data)
    cap_notional_back_run_bound = market.backRunBound(data)

    # expect is the min of all cap quantities
    expect = min(cap_notional, cap_notional_front_run_bound,
                 cap_notional_back_run_bound)
    actual = market.capNotionalAdjustedForBounds(data, cap_notional)
    assert actual == expect


def test_cap_notional_adjusted_for_bounds_when_no_reserve(market, feed):
    # Test cap notional adjustments is min of all bounds and circuit breaker
    idx = RiskParameter.CAP_NOTIONAL.value
    cap_notional = market.params(idx)
    data = (1642797758, 600, 3600, 2729583770051358617413,
            2739701430255362520176, 2729583770051358617413,
            1909229154186640322863637, False)  # has_reserve = False

    # check cap adjusted for bounds is cap_notional when no reserve
    expect = cap_notional
    actual = market.capNotionalAdjustedForBounds(data, cap_notional)
    assert actual == expect


# NOTE: strategy min/max rely on circuitBreakerMintTarget set in conftest.py
@given(
    minted=strategy('decimal', min_value='66670', max_value='133340',
                    places=1))
def test_cap_notional_circuit_breaker(market, minted):
    idx_notional = RiskParameter.CAP_NOTIONAL.value
    idx_target = RiskParameter.CIRCUIT_BREAKER_MINT_TARGET.value

    cap_notional = market.params(idx_notional)
    target = market.params(idx_target)

    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capNotional
    expect = int(cap_notional * (2 - minted / target))
    actual = market.circuitBreaker(snapshot, cap_notional)
    assert int(actual) == approx(expect)


# NOTE: strategy min/max rely on circuitBreakerMintTarget set in conftest.py
@given(
    minted=strategy('decimal', min_value='-133340', max_value='66670',
                    places=1))
def test_cap_notional_circuit_breaker_when_minted_less_than_target(market,
                                                                   minted):
    idx = RiskParameter.CAP_NOTIONAL.value
    cap_notional = market.params(idx)

    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capNotional
    expect = cap_notional
    actual = market.circuitBreaker(snapshot, cap_notional)
    assert actual == expect


# NOTE: strategy min/max rely on circuitBreakerMintTarget set in conftest.py
@given(
    minted=strategy('decimal', min_value='133340', max_value='266680',
                    places=1))
def test_cap_notional_circuit_breaker_when_mint_greater_than_2x_target(market,
                                                                       minted):
    idx = RiskParameter.CAP_NOTIONAL.value
    cap_notional = market.params(idx)

    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capNotional
    expect = 0
    actual = market.circuitBreaker(snapshot, cap_notional)
    assert actual == expect


def test_cap_oi_adjusted_for_circuit_breaker(market, feed):
    # Test cap oi circuit adjustment is min cap notional and
    # circuit breaker
    idx = RiskParameter.CAP_NOTIONAL.value
    cap_notional = market.params(idx)
    mid_price = 100000000000000000000  # 100
    cap_oi = int(Decimal(cap_notional) * Decimal(1e18) / Decimal(mid_price))
    snapshot = market.snapshotMinted()

    # calculate cap oi adjusted for circuit breaker
    cap_oi_circuit_breaker = market.circuitBreaker(snapshot, cap_oi)

    # expect is the min of all cap quantities
    expect = min(cap_oi, cap_oi_circuit_breaker)
    actual = market.capOiAdjustedForCircuitBreaker(cap_oi)
    assert actual == expect


def test_cap_oi_adjusted_for_circuit_breaker_after_mint(
        ovl, alice, rando, mock_market, mock_feed, factory, gov):
    # set circuit breaker mint target much lower to see effects
    idx_mint = RiskParameter.CIRCUIT_BREAKER_MINT_TARGET.value
    mint_target = int(Decimal(1000) * Decimal(1e18))
    factory.setRiskParam(mock_feed, idx_mint, mint_target, {"from": gov})

    # position build attributes
    notional_initial = Decimal(1000)
    leverage = Decimal(1.5)

    # calculate expected pos info data
    idx_trade = RiskParameter.TRADING_FEE_RATE.value
    trading_fee_rate = Decimal(mock_market.params(idx_trade) / 1e18)
    collateral, _, _, trade_fee \
        = calculate_position_info(notional_initial, leverage, trading_fee_rate)

    # input values for build
    input_collateral = int(collateral * Decimal(1e18))
    input_leverage = int(leverage * Decimal(1e18))
    input_is_long = True

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 2**256-1

    # approve collateral amount: collateral + trade fee
    approve_collateral = int((collateral + trade_fee) * Decimal(1e18))

    # approve then build
    # NOTE: build() tests in test_build.py
    ovl.approve(mock_market, approve_collateral, {"from": alice})
    tx = mock_market.build(input_collateral, input_leverage, input_is_long,
                           input_price_limit, {"from": alice})
    pos_id = tx.return_value

    # set price to something significantly larger
    price_multiplier = Decimal(2.5)
    price = Decimal(mock_feed.price()) * price_multiplier
    mock_feed.setPrice(price, {"from": rando})

    # input values for unwind
    input_pos_id = pos_id
    input_fraction = int(Decimal(1e18))

    # NOTE: slippage tests in test_slippage.py
    # NOTE: setting to min/max here, so never reverts with slippage>max
    input_price_limit = 0

    # unwind fraction of shares
    tx = mock_market.unwind(input_pos_id, input_fraction, input_price_limit,
                            {"from": alice})

    # Test cap oi circuit adjustment is min cap notional and
    # circuit breaker
    idx_notional = RiskParameter.CAP_NOTIONAL.value
    cap_notional = mock_market.params(idx_notional)
    cap_oi = int(Decimal(cap_notional) * Decimal(1e18) / Decimal(price))
    snapshot = mock_market.snapshotMinted()

    # calculate cap oi adjusted for circuit breaker
    cap_oi_circuit_breaker = mock_market.circuitBreaker(snapshot, cap_oi)

    # expect is the min of all cap quantities
    expect = min(cap_oi, cap_oi_circuit_breaker)
    actual = mock_market.capOiAdjustedForCircuitBreaker(cap_oi)
    assert actual == expect


def test_oi_from_notional(market, feed):
    idx = RiskParameter.CAP_NOTIONAL.value
    cap_notional = market.params(idx)
    data = feed.latest()

    # oi cap should be cap notional / mid, with zero volume assumption on
    # mid so cap is dependent on only underlying feed price
    mid = mid_from_feed(data)
    cap_oi = Decimal(cap_notional) / Decimal(mid)

    expect = int(cap_oi * Decimal(1e18))
    actual = market.oiFromNotional(cap_notional, mid)
    assert int(actual) == approx(expect)
