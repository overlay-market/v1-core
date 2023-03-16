import click

from scripts.load_feed_parameters import get_parameters
from brownie import accounts, network, Contract

def main():
    """
    Deploys a new OverlayV1ChainlinkFeed contract, and actual market 
    from OverlayV1Factory contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    parameters = get_parameters()

    click.echo("Getting all parameters")
    dev = accounts.load(1) # will prompt you to enter password on terminal
    aggregator = parameters["mcap1000"]['aggregator']
    risk_parameters = parameters["mcap1000"]['risk_parameters']
    overlay_v1_factory_address = parameters["mcap1000"]['overlay_v1_factory_address']
    overlay_v1_chainlink_feed_factory_contract_address = parameters[
        "mcap1000"]['overlay_v1_chainlink_feed_factory_contract_address']

    # connect to overlay v1 chainlink feed factory contract
    overlay_v1_chainlink_feed_factory_contract = Contract.from_explorer(
        f"{overlay_v1_chainlink_feed_factory_contract_address}")

    # get feed address
    feed_contract_address = overlay_v1_chainlink_feed_factory_contract.deployFeed.call(
        aggregator, {"from": dev})

    # deploy feed
    click.echo("Deploying Chainlink Feed")
    overlay_v1_chainlink_feed_factory_contract.deployFeed(
        aggregator, {"from": dev})
    click.echo(f"Chainlink Feed deployed [{feed_contract_address}]")

    # connect to overlay v1 factory contract
    overlay_v1_factory_contract = Contract.from_explorer(
        f'{overlay_v1_factory_address}')

    # get market address
    market = overlay_v1_factory_contract.deployMarket.call(
        overlay_v1_chainlink_feed_factory_contract_address,feed_contract_address,risk_parameters,
        {"from": dev})

    # deploy market
    click.echo("Deploying Chainlink Market")
    overlay_v1_factory_contract.deployMarket(
        overlay_v1_chainlink_feed_factory_contract_address,feed_contract_address,risk_parameters,
        {"from": dev})

    click.echo(f"Market deployed [{market}]")
