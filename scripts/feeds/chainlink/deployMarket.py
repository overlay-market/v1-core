import click
from brownie import accounts, network, Contract
from scripts.overlay_management import OM
from scripts import utils


def main(dev, chain_id, new_feed_factory_flag):
    """
    Deploys a market from OverlayV1Factory contract
    """
    click.echo(f"Commence market deployment")
    click.echo(f"You are using the '{network.show_active()}' network")
    deployable_markets = OM.get_deployable(chain_id, 'market')

    click.echo("Getting all parameters")
    afap = OM.get_all_parameters(chain_id)

    for dm in deployable_markets:
        # Get address of factory corresponding to chain
        factory_addr = OM.const_addresses[chain_id]['factory']
        factory_abi = utils.get_abi(chain_id, factory_addr)

        # Load contract object using factory's address and abi
        factory = Contract.from_abi('factory', factory_addr, factory_abi)




    # for key, chain_dict in deployable_feeds.items():
    #     #TODO FIX THE BELOW TO LOOP THROUGH ALL ORACLES
    #     oracle_feed =  OM.getKey(chain_dict[chain_id])
    #     if OM.MARKET_ADDRESS not in chain_dict[chain_id][oracle_feed]:
    #         parameters = OM.get_feed_network_parameters(key, chain_id, oracle_feed)
    #         aggregator = parameters[0]
    #         risk_parameters = parameters[4]
    #         overlay_factory_address = parameters[2]
    #         overlay_chainlink_feed_factory_contract_address = parameters[3]

    #         # connect to overlay v1 chainlink feed factory contract
    #         overlay_chainlink_feed_factory_contract = Contract.from_explorer(
    #             f"{overlay_chainlink_feed_factory_contract_address}")

    #         # connect to overlay v1 factory contract
    #         overlay_factory_contract = Contract.from_explorer(
    #             f'{overlay_factory_address}')

    #         # get feed address
    #         feed_contract_address = overlay_chainlink_feed_factory_contract.getFeed(aggregator)

    #         # get market address
    #         market = overlay_factory_contract.deployMarket.call(
    #             overlay_chainlink_feed_factory_contract_address,feed_contract_address,risk_parameters,
    #             {"from": dev})

    #         # deploy market
    #         click.echo("Deploying Chainlink Market")
    #         overlay_factory_contract.deployMarket(
    #             overlay_chainlink_feed_factory_contract_address,feed_contract_address,risk_parameters,
    #             {"from": dev, "maxFeePerGas": 3674000000})

    #         click.echo(f"Market deployed [{market}]")

    #         deployed_markets.append((market, chain_id, oracle_feed))
    #         all_feeds_all_parameters[key][chain_id][oracle_feed][OM.MARKET_ADDRESS] = f'{market}'
    #         data = all_feeds_all_parameters
    #         OM.update_feeds_with_market_parameter(data)


    # return deployed_markets