from brownie import reverts, OverlayV1FeedMock


def test_deploy_feed_reverts_when_micro_window_zero(rando):
    micro_window = 0
    macro_window = 3600
    price = 1000000000000000000
    reserve = 2000000000000000000000000

    with reverts("OVLV1Feed: microWindow == 0"):
        _ = rando.deploy(OverlayV1FeedMock, micro_window, macro_window,
                         price, reserve)


def test_deploy_feed_reverts_when_macro_lt_micro(rando):
    macro_window = 3600
    price = 1000000000000000000
    reserve = 2000000000000000000000000

    # check reverts when micro > macro
    micro_window = 3601
    with reverts("OVLV1Feed: macroWindow < microWindow"):
        _ = rando.deploy(OverlayV1FeedMock, micro_window, macro_window,
                         price, reserve)

    # check succeeds when micro == macro
    micro_window = macro_window
    _ = rando.deploy(OverlayV1FeedMock, micro_window, macro_window,
                     price, reserve)


def test_deploy_feed_reverts_when_macro_gt_1_day(rando):
    micro_window = 3600
    price = 1000000000000000000
    reserve = 2000000000000000000000000

    # check reverts when macro > 1d
    macro_window = 86401
    with reverts("OVLV1Feed: macroWindow > 1 day"):
        _ = rando.deploy(OverlayV1FeedMock, micro_window, macro_window,
                         price, reserve)

    # check succeeds when macro <= 1d
    macro_window = 86400
    _ = rando.deploy(OverlayV1FeedMock, micro_window, macro_window,
                     price, reserve)
