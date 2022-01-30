from decimal import Decimal
from pytest import approx
from brownie.test import given, strategy


def test_cap_oi_front_run_bound(market, feed):
    lmbda = Decimal(market.lmbda()) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    # TODO: generalize for any feed
    _, _, _, _, _, _, _, reserve_micro, _, _ = data

    # check front run bound is lmbda * reserveOverMicro / 2 when has reserve
    expect = int(lmbda * Decimal(reserve_micro) / Decimal(2))
    actual = market.capOiFrontRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_oi_front_run_bound_when_no_reserve(market, feed):
    cap_oi = market.capOi()
    data = (1642797758, 600, 3600, 2729583770051358617413,
            2739701430255362520176, 2729583770051358617413,
            2739701430255362520176, 1918499886987334209868033,
            1909229154186640322863637, False)  # has_reserve = False

    # check front run bound is cap_oi when no reserve
    expect = cap_oi
    actual = market.capOiFrontRunBound(data)
    assert actual == expect


def test_cap_oi_back_run_bound(market, feed):
    delta = Decimal(market.delta()) / Decimal(1e18)
    data = feed.latest()

    # NOTE: assumes using UniswapV3 feed with hasReserve = true
    # TODO: generalize for any feed
    average_block_time = 14
    _, _, macro_window, _, _, _, _, reserve_micro, _, _ = data

    # check front run bound is lmbda * reserveOverMicro / 2 when has reserve
    window = Decimal(macro_window) / Decimal(average_block_time)
    expect = int(Decimal(2) * delta * Decimal(reserve_micro) * window)
    actual = market.capOiBackRunBound(data)
    assert int(actual) == approx(expect)


def test_cap_oi_back_run_bound_when_no_reserve(market):
    cap_oi = market.capOi()
    data = (1642797758, 600, 3600, 2729583770051358617413,
            2739701430255362520176, 2729583770051358617413,
            2739701430255362520176, 1918499886987334209868033,
            1909229154186640322863637, False)  # has_reserve = False

    # check back run bound is cap_oi when no reserve
    expect = cap_oi
    actual = market.capOiBackRunBound(data)
    assert actual == expect


# NOTE: strategy min/max rely on circuitBreakerMintTarget set in conftest.py
@given(
    minted=strategy('decimal', min_value='66670', max_value='133340',
                    places=1))
def test_cap_oi_circuit_breaker(market, minted):
    cap_oi = market.capOi()
    target = market.circuitBreakerMintTarget()

    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capOi
    expect = int(cap_oi * (2 - minted / target))
    actual = market.capOiCircuitBreaker(snapshot)
    assert int(actual) == approx(expect)


# NOTE: strategy min/max rely on circuitBreakerMintTarget set in conftest.py
@given(
    minted=strategy('decimal', min_value='-133340', max_value='66670',
                    places=1))
def test_cap_oi_circuit_breaker_when_minted_less_than_target(market, minted):
    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capOi
    expect = market.capOi()
    actual = market.capOiCircuitBreaker(snapshot)
    assert actual == expect


# NOTE: strategy min/max rely on circuitBreakerMintTarget set in conftest.py
@given(
    minted=strategy('decimal', min_value='133340', max_value='266680',
                    places=1))
def test_cap_oi_circuit_breaker_when_minted_greater_than_2x_target(market,
                                                                   minted):

    # assemble Roller.snapshot struct
    timestamp = 1643247197
    window = 2592000
    minted = int(minted * Decimal(1e18))
    snapshot = (timestamp, window, minted)

    # check breaker bound returns capOi
    expect = 0
    actual = market.capOiCircuitBreaker(snapshot)
    assert actual == expect


def test_cap_oi_with_adjustments(market, feed):
    # Test cap oi adjustments is min of all bounds and circuit breaker
    cap_oi = market.capOi()
    data = feed.latest()
    snapshot = market.snapshotMinted()

    # calculate all cap oi bounds:
    # 1. front run bound; 2. back run bound; 3. circuit breaker
    cap_oi_front_run_bound = market.capOiFrontRunBound(data)
    cap_oi_back_run_bound = market.capOiBackRunBound(data)
    cap_oi_circuit_breaker = market.capOiCircuitBreaker(snapshot)

    # expect is the min of all cap quantities
    expect = min(cap_oi, cap_oi_front_run_bound, cap_oi_back_run_bound,
                 cap_oi_circuit_breaker)
    actual = market.capOiWithAdjustments(data)
    assert actual == expect
