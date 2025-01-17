import click

from brownie import OverlayV1Token, OverlayV1Factory, accounts, network, web3
from hexbytes import HexBytes


# governance multisig
# TODO: change
GOV = "0x95f972fc4D17a0D343Cd5eaD8d6DCBef5606CA66"

# fee recipient address
# TODO: change
FEE_RECIPIENT = "0xDFafdfF09C1d63257892A8d2F56483588B99315A"

# ROLES
ADMIN = "ADMIN"
GOVERNOR = "GOVERNOR"
MINTER = "MINTER"
BURNER = "BURNER"


def _role(name):
    if name == ADMIN:
        return HexBytes("0x00")
    return web3.solidityKeccak(['string'], [name])


def main():
    """
    Deploys new OverlayV1Token and OverlayV1Factory contracts.

    Grants token admin rights to the factory to enable deploying of markets
    with mint and burn priveleges. Grants token admin rights to governor and
    renounces all token rights for deployer.
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # deploy OVL
    ovl = OverlayV1Token.deploy({"from": dev}, publish_source=True)
    click.echo(f"OVL Token deployed [{ovl.address}]")

    # deploy market factory
    factory = OverlayV1Factory.deploy(
        ovl, FEE_RECIPIENT, {"from": dev}, publish_source=True)
    click.echo(f"Factory deployed [{factory.address}]")

    # grant market factory admin role to grant minter + burner roles to markets
    # on deployMarket calls
    ovl.grantRole(_role(ADMIN), factory, {"from": dev})

    # grant admin rights to gov
    ovl.grantRole(_role(ADMIN), GOV, {"from": dev})
    ovl.grantRole(_role(MINTER), GOV, {"from": dev})
    ovl.grantRole(_role(GOVERNOR), GOV, {"from": dev})
    click.echo(f"OVL Token roles granted to [{GOV}]")

    # renounce admin rights so only gov has roles
    ovl.renounceRole(_role(ADMIN), dev, {"from": dev})
