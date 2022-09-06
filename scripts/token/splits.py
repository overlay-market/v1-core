import click

from brownie import OverlayV1Token, accounts, network, web3, interface
from hexbytes import HexBytes

# RECIPIENTS = [ (accounts[i], i+1) for i in range(10) ]

SPLITS = "0x2ed6c4B5dA6378c7897AC67Ba9e43102Feb694EE"

ADMIN = "ADMIN"
GOVERNOR = "GOVERNOR"
MINTER = "MINTER"
BURNER = "BURNER"
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

    split_recipient_2 = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # total_shares = 0 
    # for i in range(len(RECIPIENTS)):
    #   total_shares += RECIPIENTS[i][1]

    # recipients = []
    # percents = []
    # totaled = 0
    # for i in range(len(RECIPIENTS)):
    #   percent = ( RECIPIENTS[i][1] / total_shares ) * 1e5
    #   print(percent)
    #   totaled += percent
    #   recipients.append(RECIPIENTS[i][0])
    #   percents.append(int(percent))
    #
    # print("totaled", totaled)
    # print("recipients", recipients)
    # print("percents", percents)

    splits = getattr(interface, 'ISplitMain')(SPLITS)
    print("splits", splits)


    recipients = [ dev, split_recipient_2 ]
    percents = [ 5e5, 5e5 ]

    recipients.sort(key=lambda x: x.address)

    tx = splits.createSplit(recipients, 
        percents, 0, dev, { 'from':dev })
    click.echo(f"Split Contract Created")

    split = tx.events['CreateSplit']['split']

    # deploy OVL
    ovl = OverlayV1Token.deploy({"from": dev}, publish_source=True)
    click.echo(f"OVL Token deployed [{ovl.address}]")

    ovl.grantRole(role(MINTER), dev, {"from": dev})
    click.echo(f"Deployer address granted minting permissions")

    ovl.mint(split, 1e18, {'from': dev})
    click.echo(f"Minted 1e18 to splits contract")

    tx = splits.distributeERC20(split, ovl, recipients, 
        percents, 0, dev, {'from': dev})
    click.echo(f"Distributed ERC20 from split contract")

    tx = splits.withdraw(dev, 0, [ovl], { 'from': dev })
    click.echo(f"Withdrew deployer's portion from split")

