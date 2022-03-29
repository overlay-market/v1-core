def test_sub_floor(fixed_point):
    a = 100000000000000000000  # 100
    b = 20000000000000000000  # 20

    expect = 80000000000000000000  # 80
    actual = fixed_point.subFloor(a, b)
    assert expect == actual


def test_sub_floor_when_a_gt_b(fixed_point):
    a = 20000000000000000000  # 20
    b = 100000000000000000000  # 100

    expect = 0
    actual = fixed_point.subFloor(a, b)
    assert expect == actual


def test_sub_floor_when_a_equals_b(fixed_point):
    a = 20000000000000000000  # 20
    b = 20000000000000000000  # 20

    expect = 0
    actual = fixed_point.subFloor(a, b)
    assert expect == actual
