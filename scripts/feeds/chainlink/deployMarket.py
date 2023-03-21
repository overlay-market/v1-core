import click
from scripts.overlay_management import OM
from brownie import accounts, network, Contract

def main():
    """
    Deploys a market from OverlayV1Factory contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    deployable_feeds = OM.filter_by_deployable([True])
    all_feeds_all_parameters = OM.get_all_feeds_all_parameters()

    click.echo("Getting all parameters")
    dev = accounts.load(1) # will prompt you to enter password on terminal

    for key, chain_dict in deployable_feeds.items():
        for chain_key in chain_dict:
            feed_oracle = OM.getKey(chain_dict[chain_key])
            if 'market' not in chain_dict[chain_key][feed_oracle]:
                parameters = OM.get_feed_network_parameters(key, chain_key, feed_oracle)
                aggregator = parameters[0]
                risk_parameters = parameters[4]
                overlay_v1_factory_address = parameters[2]
                overlay_v1_chainlink_feed_factory_contract_address = parameters[3]

                # connect to overlay v1 chainlink feed factory contract
                overlay_v1_chainlink_feed_factory_contract = Contract.from_explorer(
                    f"{overlay_v1_chainlink_feed_factory_contract_address}")

                # connect to overlay v1 factory contract
                overlay_v1_factory_contract = Contract.from_explorer(
                    f'{overlay_v1_factory_address}')

                # get feed address
                feed_contract_address = overlay_v1_chainlink_feed_factory_contract.getFeed(aggregator)

                # get market address
                market = overlay_v1_factory_contract.deployMarket.call(
                    overlay_v1_chainlink_feed_factory_contract_address,feed_contract_address,risk_parameters,
                    {"from": dev})

                # deploy market
                click.echo("Deploying Chainlink Market")
                overlay_v1_factory_contract.deployMarket(
                    overlay_v1_chainlink_feed_factory_contract_address,feed_contract_address,risk_parameters,
                    {"from": dev, "maxFeePerGas": 3674000000})

                click.echo(f"Market deployed [{market}]")
            
                all_feeds_all_parameters[key][chain_key][feed_oracle]['market'] = f'{market}'
                data = all_feeds_all_parameters
                OM.update_feeds_with_market_parameter(data)
            
