import click

from scripts.load_feed_parameters import get_parameters
from brownie import OverlayV1ChainlinkFeedFactory, accounts, network, Contract


def main():
    """
    Deploys a new OverlayV1ChainlinkFeedFactory contract, which allows for
    permissionless deployment of OverlayV1Chainlink feeds.
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    parameters = get_parameters()

    click.echo("Getting all parameters")
    dev = accounts.load('name of saved address') # will prompt you to enter password on terminal
    macro_window = parameters["mcap1000"]['macroWindow']
    micro_window = parameters["mcap1000"]['microWindow']
    overlay_v1_factory_address = parameters["mcap1000"]['overlay_v1_factory_address']

    # deploy feed factory
    click.echo("Deploying Chainlink Feed Factory")
    feed_factory = OverlayV1ChainlinkFeedFactory.deploy(
        micro_window,macro_window, {"from": dev}, publish_source=True)
    click.echo(f"Chainlink Feed Factory deployed [{feed_factory.address}]")

    overlay_v1_factory_contract = Contract.from_explorer(
        overlay_v1_factory_address)

    # add factory
    click.echo("Adding Chainlink Feed Factory Address on Overlay V1 Factory Contract")
    overlay_v1_factory_contract.addFeedFactory(feed_factory, {"from": dev})
    click.echo("Feed Factory added to OverlayV1Factory")
