from pytest import approx


def test_consult_for_daiweth(pool_daiweth_30bps, quanto_feed):
    seconds_agos = [3600, 600, 0]
    tick_cums, secs_per_liq_cums = pool_daiweth_30bps.observe(seconds_agos)
    actual_avg_ticks, actual_avg_liqs = quanto_feed.consult(pool_daiweth_30bps,
                                                            seconds_agos)

    # calculate expect arithmetic means for ticks and harmonic
    # mean for liquidity to compare w actuals
    for i in range(2):
        expect_avg_tick = int((tick_cums[-1]-tick_cums[i])/seconds_agos[i])
        expect_avg_liq = int(seconds_agos[i] * ((1 << 160) - 1) /
                             ((secs_per_liq_cums[-1] - secs_per_liq_cums[i])
                             << 32))

        # TODO: determine if its a problem rel=1e-4 is needed
        # or just a rounding issue?
        assert approx(expect_avg_tick, rel=1e-4) == actual_avg_ticks[i]
        assert approx(expect_avg_liq) == actual_avg_liqs[i]


def test_consult_for_uniweth(pool_uniweth_30bps, inverse_feed):
    seconds_agos = [3600, 600, 0]
    tick_cums, secs_per_liq_cums = pool_uniweth_30bps.observe(seconds_agos)
    actual_avg_ticks, actual_avg_liqs = inverse_feed.consult(
        pool_uniweth_30bps, seconds_agos)

    # calculate expect arithmetic means for ticks and harmonic
    # mean for liquidity to compare w actuals
    for i in range(2):
        expect_avg_tick = int((tick_cums[-1]-tick_cums[i])/seconds_agos[i])
        expect_avg_liq = int(seconds_agos[i] * ((1 << 160) - 1) /
                             ((secs_per_liq_cums[-1] - secs_per_liq_cums[i])
                             << 32))

        # TODO: determine if its a problem rel=1e-4 is needed
        # or just a rounding issue?
        assert approx(expect_avg_tick, rel=1e-4) == actual_avg_ticks[i]
        assert approx(expect_avg_liq) == actual_avg_liqs[i]
