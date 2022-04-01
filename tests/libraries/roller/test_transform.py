from pytest import approx
from brownie import chain
from brownie.test import given, strategy
from decimal import Decimal


@given(
    accumulator_last=strategy('decimal', min_value='-10000000.000',
                              max_value='10000000.000', places=3),
    window_last=strategy('uint256', min_value='10000', max_value='7776000'),
    value=strategy('decimal', min_value='-10000000.000',
                   max_value='10000000.000', places=3),
    window=strategy('uint256', min_value='10000', max_value='7776000'),
    dt=strategy('uint256', min_value='0', max_value='10000'))
def test_transform(roller, accumulator_last, window_last, value, window, dt):
    """
    Tests (success) for transform when
    dt = block.timestamp - timestampLast < windowLast
    """
    accumulator_last = int(accumulator_last * Decimal(1e18))
    timestamp_last = chain[-1]['timestamp'] - dt
    value = int(value * Decimal(1e18))
    now = chain[-1]['timestamp']

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # expect accumulator now to be calculated as
    # accumulatorLast * (1 - dt/windowLast) + value to decay toward zero
    accumulator_last_decayed = accumulator_last * (1 - dt/window_last)
    expect_value = int(accumulator_last_decayed + value)

    # expect window now to be calculated as weighted average
    # of remaining time left in last window and total time in new window
    # weights are accumulator values for the respective time window
    w1 = abs(accumulator_last_decayed)
    w2 = abs(value)
    expect_window = int(((window_last - dt) * w1 + window * w2) / (w1 + w2)) \
        if expect_value != 0 else window

    # expect timestamp is just now
    expect_timestamp = now

    actual = roller.transform(snapshot, now, window, value)
    (actual_timestamp, actual_window, actual_value) = actual

    assert actual_timestamp == expect_timestamp
    # approx to 1s absolute to account for rounding errors
    # TODO: fix rounding issues here instead of approx
    assert int(actual_window) == approx(expect_window, abs=1)  # tol to 1s
    assert int(actual_value) == approx(expect_value)


def test_transform_when_last_window_passed(roller):
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # check after windowLast has passed, all accumulatorLast has decayed
    # to zero. Should return just (value, window)
    expect = (now, window, value)
    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect


def test_transform_when_last_accumulator_zero(roller):
    # accumulatorLast == 0 edge case occurs before first write to
    # rolling values
    accumulator_last = 0  # 0% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # Check transform simply returns (window, value)
    expect = (now, window, value)
    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect


def test_transform_when_now_accumulator_zero(roller):
    # accumulatorLast == 0 edge case occurs before first write to
    # rolling values
    accumulator_last = 0  # 0% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 0  # 0% of cap
    now = chain[-1]['timestamp']
    window = 600

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # Check transform simply returns (value, window)
    expect = (now, window, value)
    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect


def test_transform_when_last_window_zero(roller):
    # windowLast == 0 edge case occurs before first write to rolling values
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 0
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # Check transform simply returns (value, window) to avoid
    # div by zero errors
    expect = (now, window, value)
    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect


def test_transform_when_last_timestamp_zero(roller):
    # timestampLast == 0 edge case occurs before first write to rolling values
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = 0
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # Check transform simply returns (value, window)
    expect = (now, window, value)
    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect


def test_transform_when_timestamp_32_wraps(roller):
    # timestampLast == 0 edge case occurs before first write to rolling values
    accumulator_last = 200000000000000000  # 20% of cap
    dt = 100
    now = 2**32 + 10
    timestamp_last = now - dt
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    window = 600

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # calculate the new snapshot state accumulator value
    accumulator_last_decayed = accumulator_last * (1 - dt / window_last)
    expect_accumulator = int(accumulator_last_decayed + value)

    # calculate the new snapshot state window value
    w1 = abs(accumulator_last_decayed)
    w2 = abs(value)
    expect_window = int((w1 * (window_last - dt) + w2 * window) / (w1 + w2))

    # Check actual == expect
    expect_timestamp = int(now % 2**32)
    actual = roller.transform(snapshot, now, window, value)
    (actual_timestamp, actual_window, actual_accumulator) = actual

    assert actual_timestamp == expect_timestamp
    assert int(actual_window) == approx(expect_window)
    assert int(actual_accumulator) == approx(expect_accumulator)
