from pytest import approx
from brownie import reverts
from decimal import Decimal


def test_calc_entry_to_mid_ratio(position, mid_resolution):
    entry_price = 100000000000000000000  # 100

    # check when mid price less than entry price (longs)
    mid_price = 99000000000000000000  # 99
    expect = int(Decimal(entry_price)
                 * Decimal(mid_resolution) / Decimal(mid_price))
    actual = position.calcEntryToMidRatio(entry_price, mid_price)
    assert expect == actual

    # check when mid price greater than entry price (shorts)
    mid_price = 101000000000000000000  # 101
    expect = int(Decimal(entry_price)
                 * Decimal(mid_resolution) / Decimal(mid_price))
    actual = position.calcEntryToMidRatio(entry_price, mid_price)
    assert expect == actual


def test_calc_entry_to_mid_ratio_reverts_when_entry_gt_2x_mid(position,
                                                              mid_resolution):
    mid_price = 50000000000000000000  # 50

    # check fails when entryPrice > 2 * mid
    entry_price = 100000000000000000001  # > 100
    with reverts("OVLV1: value == 0 at entry"):
        position.calcEntryToMidRatio(entry_price, mid_price)

    # check returns when entryPrice == 2 * mid
    entry_price = 100000000000000000000  # 100
    expect = int(Decimal(entry_price)
                 * Decimal(mid_resolution) / Decimal(mid_price))
    actual = position.calcEntryToMidRatio(entry_price, mid_price)
    assert expect == actual


def test_get_entry_to_mid_ratio(position, mid_resolution):
    entry_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # check long (entry > mid)
    is_long = True
    mid_price = 149000000000000000000  # 149
    oi = int((Decimal(notional) / Decimal(mid_price))
             * Decimal(1000000000000000000))  # ~ 0.067

    # NOTE: calcEntryToMidRatio tested above
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = Decimal(mid_ratio) * Decimal(1e18) / Decimal(mid_resolution)
    actual = position.getEntryToMidRatio(pos)
    assert expect == actual

    # check short (entry < mid)
    is_long = False
    mid_price = 151000000000000000000  # 151
    oi = int((Decimal(notional) / Decimal(mid_price))
             * Decimal(1000000000000000000))  # ~ 0.067

    # NOTE: calcEntryToMidRatio tested above
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = Decimal(mid_ratio) * Decimal(1e18) / Decimal(mid_resolution)
    actual = position.getEntryToMidRatio(pos)
    assert expect == actual


def test_entry_price(position):
    entry_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    # check long (entry > mid)
    is_long = True
    mid_price = 149000000000000000000  # 149
    oi = int((Decimal(notional) / Decimal(mid_price))
             * Decimal(1000000000000000000))  # ~ 0.067

    # NOTE: calcEntryToMidRatio tested above
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    expect = entry_price
    actual = position.entryPrice(pos)
    assert expect == approx(actual)

    # check short (entry < mid)
    is_long = False
    mid_price = 151000000000000000000  # 151
    oi = int((Decimal(notional) / Decimal(mid_price))
             * Decimal(1000000000000000000))  # ~ 0.067

    # NOTE: calcEntryToMidRatio tested above
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)

    expect = entry_price
    actual = position.entryPrice(pos)
    assert expect == approx(actual)


def test_entry_price_when_oi_is_zero(position):
    entry_price = 150000000000000000000  # 150
    notional = 10000000000000000000  # 10
    debt = 2000000000000000000  # 2
    liquidated = False

    is_long = True
    mid_price = 149000000000000000000  # 149
    oi = 0

    # NOTE: calcEntryToMidRatio tested above
    mid_ratio = position.calcEntryToMidRatio(entry_price, mid_price)
    pos = (notional, debt, mid_ratio, is_long, liquidated, oi)
    expect = 0
    actual = position.entryPrice(pos)
    assert expect == actual
