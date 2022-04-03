from brownie import OverlayV1FeedFactoryMock, reverts


def test_deploy_factory_reverts_when_micro_window_zero(rando):
    micro_window = 0
    macro_window = 3600

    with reverts("OVLV1: microWindow == 0"):
        _ = rando.deploy(OverlayV1FeedFactoryMock, micro_window, macro_window)


def test_deploy_factory_reverts_when_macro_lt_micro(rando):
    macro_window = 3600

    # check reverts when micro > macro
    micro_window = 3601
    with reverts("OVLV1: macroWindow < microWindow"):
        _ = rando.deploy(OverlayV1FeedFactoryMock, micro_window, macro_window)

    # check succeeds when micro == macro
    micro_window = macro_window
    _ = rando.deploy(OverlayV1FeedFactoryMock, micro_window, macro_window)


def test_deploy_factory_reverts_when_macro_gt_1_day(rando):
    micro_window = 3600

    # check reverts when macro > 1d
    macro_window = 86401
    with reverts("OVLV1: macroWindow > 1 day"):
        _ = rando.deploy(OverlayV1FeedFactoryMock, micro_window, macro_window)

    # check succeeds when macro <= 1d
    macro_window = 86400
    _ = rando.deploy(OverlayV1FeedFactoryMock, micro_window, macro_window)
