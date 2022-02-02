from brownie import chain


def test_cumulative(roller):
    accumulator_last = 200000000000000000  # 20% of cap
    timestamp_last = chain[-1]['timestamp'] - 1000
    window_last = 1000

    # assemble Roller.snapshot struct
    snapshot = (timestamp_last, window_last, accumulator_last)

    # check returns accumulator_last
    expect = accumulator_last
    actual = roller.cumulative(snapshot)
    assert actual == expect
