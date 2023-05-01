from brownie import Contract, history
from scripts.overlay_management import OM
from scripts import utils


def main(safe, chain_id, all_params):
    """
    Deploys new market contracts
    """
    print(f"Commence market deployment script")
    deployable_markets = OM.get_deployable_feed_market(chain_id, 'market')
    num_to_deploy = len(deployable_markets)
    print(f'Markets to deploy: {num_to_deploy}')
    if num_to_deploy == 0:
        return

    for dm in deployable_markets:
        print(f'Commencing {dm} market deployment')
        ff_name = list(dm.keys())[0]
        dm_name = list(dm.values())[0]

        # Load factory contract
        factory = utils.load_const_contract(chain_id, OM.FACTORY_ADDRESS)

        # Get input parameters for deploying market
        risk_params = \
            list(all_params[ff_name]['markets'][dm_name]['market_parameters'].values())

        # Deploy market
        feed_addr = all_params[ff_name]['markets'][dm_name]['feed_address']
        feed_factory_addr = all_params[ff_name]['feed_factory_address']
        factory.deployMarket(
            feed_factory_addr, feed_addr, risk_params,{'from': safe.address})
        market_address = factory.getMarket(feed_addr)

        # Save address to dict
        all_params[ff_name]['markets'][dm_name]['market_address'] = market_address

    # Build multisend tx
    print(f'Batching {num_to_deploy} deployments')
    hist = history.from_sender(safe.address)
    safe_tx = safe.multisend_from_receipts(hist[-num_to_deploy:])

    # Sign and post
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)

    # Save addresses to file
    OM.update_all_parameters(all_params, chain_id)
