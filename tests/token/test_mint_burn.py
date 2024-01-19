import brownie


def test_only_minter_on_mint(token, alice, bob):
    EXPECTED_ERROR_MSG = (
        'AccessControl: account 0x33a4622b82d4c04a53e170c638b944ce27cffce3 '
        'is missing role '
        '0xf0887ba65ee2024ea881d91b74c2450ef19e1557f03bed3ea9f16b037cbe2dc9'
    )
    with brownie.reverts(EXPECTED_ERROR_MSG):
        token.mint(bob, 1 * 10 ** token.decimals(), {"from": alice})


def test_only_burner_on_burn(token, alice):
    EXPECTED_ERROR_MSG = (
        'AccessControl: account 0x33a4622b82d4c04a53e170c638b944ce27cffce3 '
        'is missing role '
        '0x9667e80708b6eeeb0053fa0cca44e028ff548e2a9f029edfeac87c118b08b7c8'
    )
    with brownie.reverts(EXPECTED_ERROR_MSG):
        token.burn(1 * 10 ** token.decimals(), {"from": alice})


def test_mint(token, minter, alice):
    before = token.balanceOf(alice)
    amount = 1 * 10 ** token.decimals()
    token.mint(alice, amount, {"from": minter})
    assert token.balanceOf(alice) == before + amount


def test_burn(token, burner, minter):
    amount = 1 * 10 ** token.decimals()
    token.mint(burner, amount, {"from": minter})
    before = token.balanceOf(burner)

    token.burn(amount, {"from": burner})
    assert token.balanceOf(burner) == before - amount


def test_mint_then_burn(token, market, alice):
    before = token.balanceOf(alice)

    token.mint(alice, 20 * 10 ** token.decimals(), {"from": market})
    mid = before + 20 * 10 ** token.decimals()
    assert token.balanceOf(alice) == mid

    before_market = token.balanceOf(market)
    token.approve(market, 20 * 10 ** token.decimals(), {"from": alice})
    token.transfer(market, 15 * 10 ** token.decimals(), {"from": alice})

    assert token.balanceOf(alice) == mid - 15 * 10 ** token.decimals()
    assert token.balanceOf(market) == \
        before_market + 15 * 10 ** token.decimals()

    token.burn(15 * 10 ** token.decimals(), {"from": market})
    assert token.balanceOf(market) == before_market

    mid_market = token.balanceOf(market)
    token.transfer(market, 5 * 10 ** token.decimals(), {"from": alice})
    assert token.balanceOf(market) == mid_market + \
        5 * 10 ** token.decimals()
    assert token.balanceOf(alice) == mid - 20 * 10 ** token.decimals()

    mid_market += 5 * 10 ** token.decimals()
    token.burn(5 * 10 ** token.decimals(), {"from": market})
    assert token.balanceOf(market) == mid_market - \
        5 * 10 ** token.decimals()
