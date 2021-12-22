def test_balances(token, gov, alice, bob, minter, burner, admin):
    assert token.totalSupply() == 2 * token.balanceOf(alice) == \
        2 * token.balanceOf(bob)
    assert token.balanceOf(gov) == 0
    assert token.balanceOf(minter) == 0
    assert token.balanceOf(burner) == 0
    assert token.balanceOf(admin) == 0


def test_roles(token, gov, minter, burner, admin, market, rando):
    assert token.hasRole(token.ADMIN_ROLE(), gov) is True
    assert token.hasRole(token.MINTER_ROLE(), minter) is True
    assert token.hasRole(token.BURNER_ROLE(), burner) is True

    assert token.hasRole(token.ADMIN_ROLE(), admin) is True

    assert token.hasRole(token.MINTER_ROLE(), market) is True
    assert token.hasRole(token.BURNER_ROLE(), market) is True

    assert token.hasRole(token.ADMIN_ROLE(), rando) is False
    assert token.hasRole(token.MINTER_ROLE(), rando) is False
    assert token.hasRole(token.BURNER_ROLE(), rando) is False


def test_erc20(token):
    assert token.decimals() == 18
    assert token.name() == "Overlay"
    assert token.symbol() == "OVL"
    assert token.totalSupply() == 8000000 * 1e18
