from brownie import reverts, OverlayV1Market


def test_deploy_creates_market(deployer, ov, feed, factory):
    # deploy the market
    tx = deployer.deploy(feed, {"from": factory})
    market_addr = tx.return_value
    market = OverlayV1Market.at(market_addr)

    # check market deployed correctly with immutables
    assert market.ov() == ov
    assert market.feed() == feed
    assert market.factory() == factory

    # test parameters reverts back to zero address
    tok, feed, fact = deployer.parameters()
    assert tok == ov
    assert feed == "0x0000000000000000000000000000000000000000"
    assert fact == factory


def test_deploy_reverts_when_not_factory(deployer, ov, feed, rando):
    # check attempting to deploy
    with reverts("OVV1: !factory"):
        deployer.deploy(feed, {"from": rando})
