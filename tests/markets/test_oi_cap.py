from decimal import Decimal
from pytest import approx
from brownie.test import given, strategy


def test_cap_notional_front_run_bound(market, feed):
    lmbda = Decimal(market.lmbda()) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    _, _, _, _, _, _, reserve_micro, _ = data

    # check front run bound is lmbda * reserveOverMicro when has reserve
    expect = int(lmbda * Decimal(reserve_micro))
    actual = market.frontRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_notional_back_run_bound(market, feed):
    delta = Decimal(market.delta()) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    average_block_time = 14
    _, _, macro_window, _, _, _, reserve_micro, _ = data

    # check back run bound is macroWindowInBlocks * reserveInOvl * 2 * delta
    # when has reserve
    window = Decimal(macro_window) / Decimal(average_block_time)
    expect = int(Decimal(2) * delta * Decimal(reserve_micro) * window)
    actual = market.backRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_notional_adjusted_for_bounds(market, feed):
    # Test cap notional adjustments is min of all bounds and circuit breaker
    cap_notional = market.capNotional()
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
    cap_notional = market.capNotional()
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
    cap_notional = market.capNotional()
    target = market.circuitBreakerMintTarget()

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
    cap_notional = market.capNotional()

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
    cap_notional = market.capNotional()

    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capNotional
    expect = 0
    actual = market.circuitBreaker(snapshot, cap_notional)
    assert actual == expect


def test_cap_notional_adjusted_for_circuit_breaker(market, feed):
    # Test cap notional circuit adjustment is min cap notional and
    # circuit breaker
    cap_notional = market.capNotional()
    snapshot = market.snapshotMinted()

    # calculate cap notional adjusted for circuit breaker
    cap_notional_circuit_breaker = market.circuitBreaker(snapshot,
                                                         cap_notional)

    # expect is the min of all cap quantities
    expect = min(cap_notional, cap_notional_circuit_breaker)
    actual = market.capNotionalAdjustedForCircuitBreaker(cap_notional)
    assert actual == expect


def test_cap_oi(market, feed):
    cap_notional = market.capNotional()
    data = feed.latest()

    # oi cap should be cap notional / mid, with zero volume assumption on
    # mid so cap is dependent on only underlying feed price
    mid = market.mid(data, 0, 0)
    cap_oi = Decimal(cap_notional) / Decimal(mid)

    expect = int(cap_oi * Decimal(1e18))
    actual = market.capOi(data, cap_notional)
    assert int(actual) == approx(expect)
