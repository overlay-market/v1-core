from brownie import chain


def test_decay_over_window(market):
    """
    Tests (success) for decayOverWindow when
    dt = block.timestamp - timestampLast < windowLast
    """
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 200
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600
    dt = 200

    # expect accumulator now to be calculated as
    # accumulatorLast * (1 - dt/windowLast) + value
    accumulator_last_decayed = accumulator_last * (1 - dt/window_last)
    expect_value_now = int(accumulator_last_decayed + value)

    # expect window now to be calculated as weighted average
    # of remaining time left in last window and total time in new window
    # weights are accumulator values for the respective time window
    numerator = int((window_last - dt) * accumulator_last_decayed
                    + window * value)
    expect_window_now = int(numerator / expect_value_now)

    expect = (expect_value_now, expect_window_now)
    actual = market.decayOverWindow(
        accumulator_last, timestamp_last, window_last, value, now, window)
    assert actual == expect


def test_decay_over_window_when_last_window_passed(market):
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # check after windowLast has passed, all accumulatorLast has decayed
    # to zero. Should return just (value, window)
    expect = (value, window)
    actual = market.decayOverWindow(
        accumulator_last, timestamp_last, window_last, value, now, window)
    assert actual == expect


def test_decay_over_window_when_last_accumulator_zero(market):
    # accumulatorLast == 0 edge case occurs before first write to
    # rolling values
    accumulator_last = 0  # 0% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # Check decayOverWindow simply returns (value, window)
    expect = (value, window)
    actual = market.decayOverWindow(
        accumulator_last, timestamp_last, window_last, value, now, window)
    assert actual == expect


def test_decay_over_window_when_now_accumulator_zero(market):
    # accumulatorLast == 0 edge case occurs before first write to
    # rolling values
    accumulator_last = 0  # 0% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 0  # 0% of cap
    now = chain[-1]['timestamp']
    window = 600

    # Check decayOverWindow simply returns (value, window)
    expect = (value, window)
    actual = market.decayOverWindow(
        accumulator_last, timestamp_last, window_last, value, now, window)
    assert actual == expect


def test_decay_over_window_when_last_window_zero(market):
    # windowLast == 0 edge case occurs before first write to rolling values
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 0
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # Check decayOverWindow simply returns (value, window) to avoid
    # div by zero errors
    expect = (value, window)
    actual = market.decayOverWindow(
        accumulator_last, timestamp_last, window_last, value, now, window)
    assert actual == expect


def test_decay_over_window_when_last_timestamp_zero(market):
    # timestampLast == 0 edge case occurs before first write to rolling values
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = 0
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600

    # Check decayOverWindow simply returns (value, window)
    expect = (value, window)
    actual = market.decayOverWindow(
        accumulator_last, timestamp_last, window_last, value, now, window)
    assert actual == expect
