import click
from dotenv import dotenv_values

from brownie import OverlayV1Token, OverlayV1Factory, accounts, network, web3
from hexbytes import HexBytes

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

    env = dotenv_values()

    GOV = env['GOVERNANCE_MULTISIG']
    FEES = env['FEE_DESTINATION']

    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # deploy OVL
    ovl = OverlayV1Token.deploy({"from": dev}, publish_source=True)
    click.echo(f"OVL Token deployed [{ovl.address}]")

    # deploy market factory
    factory = OverlayV1Factory.deploy(
        ovl, FEES, {"from": dev}, publish_source=True)
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
