def test_is_underwater_when_underwater(position):
    pass


def test_is_underwater_when_not_underwater(position):
    pass


def test_is_underwater_when_oi_zero(position):
    # TODO: should return false always since no oi
    pass


def test_is_underwater_when_leverage_one(position):
    # TODO: should return false always since no debt
    pass


def test_is_liquidatable_when_liquidatable(position):
    pass


def test_is_liquidatable_when_not_liquidatable(position):
    pass


def test_is_liquidatable_when_oi_zero(position):
    # TODO: should return false always since no oi
    pass


def test_is_liquidatable_when_leverage_one(position):
    # TODO: should return false always since no debt
    pass


def test_liquidation_price(position):
    pass


def test_liquidation_price_when_oi_zero(position):
    # TODO: should return 0 (long) or max int (short) since no oi
    pass


def test_liquidation_price_when_leverage_one(position):
    # TODO: should return 0 (long) or max int (short) since no leverage
    pass
