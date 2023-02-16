import click

from brownie import OverlayV1ChainlinkFeedFactory, accounts, network


# TODO: change
CHAINLINK_FEED_FACTORY = "0x75D6b2D432EeB742942E4f6E9FF77Db56B834099"


def main():
    """
    Creates a new OverlayV1ChainlinkFeed through feed factory
    `deployFeed()` function.
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # instantiate the feed factory contract
    feed_factory = OverlayV1ChainlinkFeedFactory.at(CHAINLINK_FEED_FACTORY)

    # assemble params for deployFeed
    params = ["_aggregator (address)",
              "_microWindow (uint256)",
              "_macroWindow (uint256)"]
    args = [click.prompt(f"{param}") for param in params]

    click.echo(
        f"""
        OverlayV1ChainlinkFeed Parameters

        aggregator (address): {args[0]}
        microWindow (uint256): {args[1]}
        macroWindow (uint256): {args[2]}
        """
    )

    if click.confirm("Deploy New Feed"):
        tx = feed_factory.deployFeed(*args, {"from": dev})
        tx.info()
        click.echo("Chainlink Feed deployed")
