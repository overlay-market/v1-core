from brownie import Contract, history
from scripts.overlay_management import OM
from scripts import utils


def main(safe, chain_id, all_params):
    """
    Deploys a market from OverlayV1Factory contract
    """
    print(f"Commence market deployment script")
    deployable_markets = OM.get_deployable(chain_id, 'market')
    num_to_deploy = len(deployable_markets)
    print(f'Markets to deploy: {num_to_deploy}')

    for dm in deployable_markets:
        print(f'Commencing {dm} market deployment')
        # Get oracle
        oracle = all_params[dm]['oracle']

        # Get required addresses corresponding to chain
        factory_addr = OM.const_addresses[chain_id]['factory']
        factory_abi = utils.get_abi(chain_id, factory_addr)

        # Load contract objects using address and abi
        factory = Contract.from_abi('factory', factory_addr, factory_abi)

        # Get input parameters for deploying market
        market_parameters = list(all_params[dm]['market_parameters'].values())

        # Deploy market
        feed_addr = all_params[dm]['feed_address']
        feed_factory_addr =\
            OM.const_addresses[chain_id]['feed_factory'][oracle]
        risk_params = list(all_params[dm]['market_parameters'].values())
        factory.deployMarket(
            feed_factory_addr, feed_addr, risk_params,{'from': safe.address})
        market_address = factory.getMarket(feed_addr)

        # Save address to dict
        all_params[dm]['market_address'] = market_address

    # Build multisend tx
    print(f'Batching {num_to_deploy} deployments')
    hist = history.from_sender(safe.address)
    safe_tx = safe.multisend_from_receipts(hist[-num_to_deploy:])

    # Sign and post
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)

    # Save addresses to file
    OM.update_all_parameters(all_params, chain_id)
