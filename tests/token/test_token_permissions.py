from brownie import reverts


def test_admin_grant_mint_role_then_revoke(token, admin, rando, minter_role):
    token.grantRole(minter_role, rando, {"from": admin})
    assert token.hasRole(minter_role, rando) is True

    token.revokeRole(minter_role, rando, {"from": admin})
    assert token.hasRole(minter_role, rando) is False


def test_admin_grant_burn_role_then_revoke(token, admin, rando, burner_role):
    token.grantRole(burner_role, rando, {"from": admin})
    assert token.hasRole(burner_role, rando) is True

    token.revokeRole(burner_role, rando, {"from": admin})
    assert token.hasRole(burner_role, rando) is False


def test_admin_grant_governor_role_then_revoke(token, admin, rando,
                                               governor_role):
    token.grantRole(governor_role, rando, {"from": admin})
    assert token.hasRole(governor_role, rando) is True

    token.revokeRole(governor_role, rando, {"from": admin})
    assert token.hasRole(governor_role, rando) is False


def test_admin_grant_guardian_role_then_revoke(token, admin, rando,
                                               guardian_role):
    token.grantRole(guardian_role, rando, {"from": admin})
    assert token.hasRole(guardian_role, rando) is True

    token.revokeRole(guardian_role, rando, {"from": admin})
    assert token.hasRole(guardian_role, rando) is False


def test_grant_roles_reverts_when_not_admin(token, rando, minter_role,
                                            burner_role, governor_role,
                                            guardian_role):
    admin_role = token.DEFAULT_ADMIN_ROLE()
    roles = [minter_role, burner_role, governor_role,
             guardian_role, admin_role]
    for role in roles:
        with reverts():
            token.grantRole(role, rando, {"from": rando})
