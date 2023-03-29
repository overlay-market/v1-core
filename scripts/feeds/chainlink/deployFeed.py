import click
from scripts.overlay_management import OM
from brownie import accounts, network, Contract
from scripts import utils


def main(acc, chain_id):
    """
    Deploys a new OverlayV1ChainlinkFeed contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")

    click.echo("Getting all parameters")
    # dev = accounts.load(acc) # will prompt you to enter password on terminal
    deployable_markets = OM.get_deployable_markets()
    afap = OM.get_all_feeds_all_parameters()

    for dm in deployable_markets:
        oracle = afap[dm]['oracle']
        chain_id = afap[dm]['chain_id']
        feed_factory_addr = OM.const_addresses[chain_id]['feed_factory'][oracle]
        feed_factory_abi = utils.get_abi(chain_id, feed_factory_addr)

        feed_factory = Contract.from_abi('feed_factory',
                                         feed_factory_addr,
                                         feed_factory_abi)


    for key, chain_dict in deployable_feeds.items():
        feed_oracle =  OM.getKey(chain_dict[chain_id])
        if OM.FEED_ADDRESS not in chain_dict[chain_id][feed_oracle]:
            parameters = OM.get_feed_network_parameters(key, chain_id, feed_oracle)
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

            all_feeds_all_parameters[key][chain_id][feed_oracle][OM.FEED_ADDRESS] = f'{777}'
            data = all_feeds_all_parameters
            OM.update_feeds_with_market_parameter(data)
