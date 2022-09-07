from pytest import approx


def test_consult_for_daiweth(pool_daiweth_30bps, quanto_feed):
    seconds_agos = [7200, 3600, 600, 0]
    windows = [3600, 3600, 600]
    now_idxs = [1, len(seconds_agos)-1, len(seconds_agos)-1]

    tick_cums, secs_per_liq_cums = pool_daiweth_30bps.observe(seconds_agos)
    actual_avg_ticks, actual_avg_liqs = quanto_feed.consult(pool_daiweth_30bps,
                                                            seconds_agos,
                                                            windows,
                                                            now_idxs)
    print("tick_cums", tick_cums)
    print("actual_avg_ticks", actual_avg_ticks)

    # calculate expect arithmetic means for ticks and harmonic
    # mean for liquidity to compare w actuals
    for i in range(len(windows)):
        expect_avg_tick = int((tick_cums[now_idxs[i]]-tick_cums[i])/windows[i])
        expect_avg_liq = int(windows[i] * ((1 << 160) - 1) /
                             ((secs_per_liq_cums[now_idxs[i]]
                              - secs_per_liq_cums[i]) << 32))

        # rel=1e-4 is needed for rounding with ticks
        assert approx(expect_avg_tick, rel=1e-4) == actual_avg_ticks[i]
        assert approx(expect_avg_liq) == actual_avg_liqs[i]


def test_consult_for_daiweth_without_reserve(pool_daiweth_30bps,
                                             quanto_feed_without_reserve):
    seconds_agos = [7200, 3600, 600, 0]
    windows = [3600, 3600, 600]
    now_idxs = [1, len(seconds_agos)-1, len(seconds_agos)-1]

    tick_cums, _ = pool_daiweth_30bps.observe(seconds_agos)
    actual_avg_ticks = quanto_feed_without_reserve.consult(pool_daiweth_30bps,
                                                           seconds_agos,
                                                           windows,
                                                           now_idxs)
    print("tick cums", tick_cums)
    print("actual avg ticks", actual_avg_ticks)

    for i in range(len(windows)):
        expect_avg_tick = int((tick_cums[now_idxs[i]]-tick_cums[i])/windows[i])
        assert approx(expect_avg_tick, rel=1e-4) == actual_avg_ticks[i]


def test_consult_for_uniweth(pool_uniweth_30bps, inverse_feed):
    seconds_agos = [7200, 3600, 600, 0]
    windows = [3600, 3600, 600]
    now_idxs = [1, len(seconds_agos)-1, len(seconds_agos)-1]

    tick_cums, secs_per_liq_cums = pool_uniweth_30bps.observe(seconds_agos)
    actual_avg_ticks, actual_avg_liqs = inverse_feed.consult(
        pool_uniweth_30bps, seconds_agos, windows, now_idxs)

    # calculate expect arithmetic means for ticks and harmonic
    # mean for liquidity to compare w actuals
    for i in range(len(windows)):
        expect_avg_tick = int((tick_cums[now_idxs[i]]-tick_cums[i])/windows[i])
        expect_avg_liq = int(windows[i] * ((1 << 160) - 1) /
                             ((secs_per_liq_cums[now_idxs[i]]
                              - secs_per_liq_cums[i]) << 32))

        # rel=1e-4 is needed for rounding with ticks
        assert approx(expect_avg_tick, rel=1e-4) == actual_avg_ticks[i]
        assert approx(expect_avg_liq) == actual_avg_liqs[i]
