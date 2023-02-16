import click

from brownie import OverlayV1ChainlinkFactory, accounts, network


def main():
    """
    Deploys a new OverlayV1ChainlinkFactory contract, which allows for
    permissionless deployment of OverlayV1ChainlinkFeed feeds.
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # assemble constructor params
    params = ["microWindow (uint256)", "macroWindow (uint256)"]
    args = [
        click.prompt(f"{param}")
        for param in params
    ]

    # deploy feed factory
    feed_factory = OverlayV1ChainlinkFactory.deploy(
        *args, {"from": dev}, publish_source=True)
    click.echo(f"Chainlink Feed Factory deployed [{feed_factory.address}]")
    click.echo("NOTE: Feed Factory is not registered in OverlayV1Factory yet!")
