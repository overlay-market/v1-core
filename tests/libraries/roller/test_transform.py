from brownie import chain


def test_transform(roller):
    """
    Tests (success) for transform when
    dt = block.timestamp - timestampLast < windowLast
    """
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 200
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600
    dt = 200
    is_negative = False

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last, is_negative)

    # expect accumulator now to be calculated as
    # accumulatorLast * (1 - dt/windowLast) + value
    accumulator_last_decayed = accumulator_last * (1 - dt/window_last)
    expect_value = int(accumulator_last_decayed + value)

    # expect window now to be calculated as weighted average
    # of remaining time left in last window and total time in new window
    # weights are accumulator values for the respective time window
    numerator = int((window_last - dt) * accumulator_last_decayed
                    + window * value)
    expect_window = int(numerator / expect_value)

    # expect timestamp is just now
    expect_timestamp = now
    expect_is_negative = is_negative

    expect = (expect_timestamp, expect_window, expect_value,
              expect_is_negative)

    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect


def test_transform_when_last_window_passed(roller):
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000
    value = 500000000000000000  # 50% of cap
    now = chain[-1]['timestamp']
    window = 600
    is_negative = False

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last, is_negative)

    # check after windowLast has passed, all accumulatorLast has decayed
    # to zero. Should return just (value, window)
    expect = (now, window, value, is_negative)
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
    is_negative = False

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last, is_negative)

    # Check transform simply returns (window, value)
    expect = (now, window, value, is_negative)
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
    is_negative = False

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last, is_negative)

    # Check transform simply returns (value, window)
    expect = (now, window, value, is_negative)
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
    is_negative = False

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last, is_negative)

    # Check transform simply returns (value, window) to avoid
    # div by zero errors
    expect = (now, window, value, is_negative)
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
    is_negative = False

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last, is_negative)

    # Check transform simply returns (value, window)
    expect = (now, window, value, is_negative)
    actual = roller.transform(snapshot, now, window, value)
    assert actual == expect
