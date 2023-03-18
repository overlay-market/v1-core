import click
from scripts.load_feed_parameters import get_parameters
from brownie import accounts, network, Contract



selected_networks = ["network1", "network2"]
filter_by_network(all_feeds_all_params, selected_networks):
    return  {market: {network: c for network, c in b.items() if network in selected_networks} for market, b in a.items()}

def main(network):
    """
    Deploys a new OverlayV1ChainlinkFeed contract, and actual market 
    from OverlayV1Factory contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    all_feeds_all_parameters = get_parameters()

    click.echo("Getting all parameters")
    dev = accounts.load('name of saved address') # will prompt you to enter password on terminal

    for key in all_feeds_all_parameters:
        if 'key_you_want_to_avoid' not in all_feeds_all_parameters[key]:
            aggregator = all_feeds_all_parameters[key]['aggregator']
            risk_parameters = all_feeds_all_parameters[key]['risk_parameters']
            overlay_v1_factory_address = all_feeds_all_parameters[key]['overlay_v1_factory_address']
            overlay_v1_chainlink_feed_factory_contract_address = all_feeds_all_parameters[key][
                'overlay_v1_chainlink_feed_factory_contract_address']

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
