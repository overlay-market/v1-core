import click
from scripts.overlay_management import OM
from brownie import accounts, network, Contract

def main():
    """
    Deploys a new OverlayV1ChainlinkFeed contract, and actual market 
    from OverlayV1Factory contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    all_feeds_all_parameters = OM.get_all_feeds_all_parameters()

    click.echo("Getting all parameters")
    dev = accounts.load(1) # will prompt you to enter password on terminal

    for key in all_feeds_all_parameters:
        if 'key_you_want_to_avoid' not in all_feeds_all_parameters[key]:
            parameters = OM.get_feed_network_parameters(key, OM.ARB_TEST, 'translucent')
            aggregator = parameters[0]
            overlay_v1_chainlink_feed_factory_contract_address = parameters[3]

            # connect to overlay v1 chainlink feed factory contract
            overlay_v1_chainlink_feed_factory_contract = Contract.from_explorer(
                f"{overlay_v1_chainlink_feed_factory_contract_address}")

            # get feed address
            feed_contract_address = overlay_v1_chainlink_feed_factory_contract.deployFeed.call(
                aggregator, {"from": dev})

            # deploy feed
            click.echo("Deploying Chainlink Feed")
            overlay_v1_chainlink_feed_factory_contract.deployFeed(
                aggregator, {"from": dev, "maxFeePerGas": 3674000000})
            click.echo(f"Chainlink Feed deployed [{feed_contract_address}]")