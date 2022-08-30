import click

from brownie import OverlayV1Token, accounts, network, web3, interface
from hexbytes import HexBytes

DISPERSE = "0xD152f549545093347A162Dce210e7293f1452150"

ADMIN = "ADMIN"
MINTER = "MINTER"
def role(name):
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

    disperse_recipient_2 = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    disperse = getattr(interface, 'IDisperse')(DISPERSE)

    recipients = [ dev, disperse_recipient_2 ]
    values = [ 5e17, 5e17 ]

    # deploy OVL
    ovl = OverlayV1Token.deploy({"from": dev}, publish_source=True)
    click.echo(f"OVL Token deployed [{ovl.address}]")

    ovl.grantRole(role(MINTER), dev, {"from": dev})
    click.echo(f"Deployer address granted minting permissions")

    ovl.mint(dev, 1e18, {'from': dev})
    click.echo(f"Minted 1e18 to deployer")

    ovl.approve(disperse, 1e18, {'from': dev})
    click.echo(f"Disperse approved for spending.")

    disperse.disperseToken(ovl, recipients, values, {'from': dev})
    click.echo(f"Dispersal accomplished.")


