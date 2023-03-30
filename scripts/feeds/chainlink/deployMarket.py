from brownie import Contract
from scripts.overlay_management import OM
from scripts import utils


def main(acc, chain_id, all_params):
    """
    Deploys a market from OverlayV1Factory contract
    """
    print(f"Commence market deployment")
    deployable_markets = OM.get_deployable(chain_id, 'market')

    for dm in deployable_markets:
        # Get required addresses corresponding to chain
        factory_addr = OM.const_addresses[chain_id]['factory']
        factory_abi = utils.get_abi(chain_id, factory_addr)

        # Load contract objects using address and abi
        factory = Contract.from_abi('factory', factory_addr, factory_abi)

        # Get input parameters for deploying market
        market_parameters = list(all_params[dm]['market_parameters'].values())

        # Deploy market
        feed_addr = all_params[dm]['feed_address']
        feed_factory_addr = OM.const_addresses[chain_id]['feed_factory']
        risk_params = list(all_params[dm]['market_parameters'].values())
        tx = factory.deployMarket(
            feed_factory_addr, feed_addr, risk_params[1:],
            {"from": acc, 'priority_fee':"2 gwei"}
        )
        market_address = factory.getMarket(feed_addr)

        # Save address
        all_params[dm]['market_address'] = market_address
        OM.update_all_parameters(all_params, chain_id)
