from brownie import reverts, OverlayV1Market


def test_deploy_creates_market(deployer, ovl, feed, factory):
    # deploy the market
    tx = deployer.deploy(feed, {"from": factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # check market deployed correctly with immutables
    assert market.ovl() == ovl
    assert market.feed() == feed
    assert market.factory() == factory

    # test parameters reverts back to zero address
    tok, feed, fact = deployer.parameters()
    assert tok == ovl
    assert feed == "0x0000000000000000000000000000000000000000"
    assert fact == factory


def test_deploy_reverts_when_not_factory(deployer, ovl, feed, rando):
    # check attempting to deploy
    with reverts("OVLV1: !factory"):
        deployer.deploy(feed, {"from": rando})
