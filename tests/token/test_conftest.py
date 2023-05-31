def test_balances(token, gov, alice, bob, minter, burner, admin):
    assert token.totalSupply() == 2 * token.balanceOf(alice) == \
        2 * token.balanceOf(bob)
    assert token.balanceOf(gov) == 0
    assert token.balanceOf(minter) == 0
    assert token.balanceOf(burner) == 0
    assert token.balanceOf(admin) == 0


def test_roles(token, gov, minter, burner, governor, admin, market,
               rando, minter_role, burner_role, governor_role):
    assert token.hasRole(token.DEFAULT_ADMIN_ROLE(), gov) is True
    assert token.hasRole(minter_role, minter) is True
    assert token.hasRole(burner_role, burner) is True
    assert token.hasRole(governor_role, governor) is True
    assert token.hasRole(token.DEFAULT_ADMIN_ROLE(), admin) is True

    assert token.hasRole(minter_role, market) is True
    assert token.hasRole(burner_role, market) is True

    assert token.hasRole(token.DEFAULT_ADMIN_ROLE(), rando) is False
    assert token.hasRole(minter_role, rando) is False
    assert token.hasRole(burner_role, rando) is False
    assert token.hasRole(governor_role, rando) is False

    assert token.getRoleAdmin(
        token.DEFAULT_ADMIN_ROLE()) == token.DEFAULT_ADMIN_ROLE()
    assert token.getRoleAdmin(minter_role) == token.DEFAULT_ADMIN_ROLE()
    assert token.getRoleAdmin(burner_role) == token.DEFAULT_ADMIN_ROLE()
    assert token.getRoleAdmin(governor_role) == token.DEFAULT_ADMIN_ROLE()


def test_erc20(token):
    assert token.decimals() == 18
    assert token.name() == "Overlay"
    assert token.symbol() == "OVL"
    assert token.totalSupply() == 8000000 * 1e18
