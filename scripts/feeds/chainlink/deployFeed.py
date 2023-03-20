import click
from scripts.overlay_management import OM
from brownie import accounts, network, Contract

def main():
    """
    Deploys a new OverlayV1ChainlinkFeed contract, and actual market 
    from OverlayV1Factory contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")

    click.echo("Getting all parameters")
    dev = accounts.load(1) # will prompt you to enter password on terminal

    deployable_feeds = OM.filter_by_deployable([True])
    all_feeds_all_parameters = OM.get_all_feeds_all_parameters()

    for key, chain_dict in deployable_feeds.items():
        for chain_key in chain_dict:
            feed_oracle = OM.getKey(chain_dict[chain_key])
            if 'feed_address' not in chain_dict[chain_key][feed_oracle]:
                parameters = OM.get_feed_network_parameters(key, chain_key, feed_oracle)
                aggregator = parameters[0]
                overlay_v1_chainlink_feed_factory_contract_address = parameters[3]

                print(aggregator,overlay_v1_chainlink_feed_factory_contract_address)

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

                all_feeds_all_parameters[key][chain_key][feed_oracle]['feed_address'] = f'{feed_contract_address}'
                data = all_feeds_all_parameters
                OM.update_feeds_with_market_parameter(data)
