import click
from scripts.overlay_management import OM
from brownie import accounts, network, Contract

def main():
    """
    Deploys a new OverlayV1ChainlinkFeed contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")

    click.echo("Getting all parameters")
    dev = accounts.load(1) # will prompt you to enter password on terminal

    all_feeds_all_parameters = OM.get_all_feeds_all_parameters()
    deployable_chains = OM.filter_by_blockchain([network.show_active()])
    deployable_feeds = OM.filter_by_deployable(deployable_chains)

    for key, chain_dict in deployable_feeds.items():
        feed_oracle =  OM.getKey(chain_dict[network.show_active()])
        if OM.FEED_ADDRESS not in chain_dict[network.show_active()][feed_oracle]:
            parameters = OM.get_feed_network_parameters(key, network.show_active(), feed_oracle)
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

            all_feeds_all_parameters[key][network.show_active()][feed_oracle][OM.FEED_ADDRESS] = f'{777}'
            data = all_feeds_all_parameters
            OM.update_feeds_with_market_parameter(data)
