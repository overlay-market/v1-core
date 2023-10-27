from scripts.overlay_management import OM
from brownie import history
from scripts import utils


def main(gov, chain_id, all_params, is_safe):
    """
    Deploys a new Feed contract
    """
    print("Commence feed deployment script")
    deployable_feeds = OM.get_deployable_feed_market(chain_id, 'feed')
    num_to_deploy = len(deployable_feeds)
    print(f'Feeds to deploy: {num_to_deploy}')
    if num_to_deploy == 0:
        return

    if is_safe:
        signer = gov.address
    else:
        signer = gov

    for df in deployable_feeds:
        print(f'Commencing {df} feed deployment')
        ff_name = list(df.keys())[0]
        df_name = list(df.values())[0]

        # Get address of feed factory corresponding to chain and oracle type
        feed_factory_addr = all_params[ff_name]['feed_factory_address']
        feed_factory = utils.load_contract(chain_id, feed_factory_addr)

        # Get input parameters for deploying feed
        feed_parameters = list(
            all_params[ff_name]['markets'][df_name]['feed_parameters'].values()
        )

        # Deploy feed and get address of deployed feed from emitted event
        tx = feed_factory.deployFeed(*feed_parameters, {'from': signer})
        feed_address = tx.events['FeedDeployed']['feed']

        # Save address to dict
        all_params[ff_name]['markets'][df_name]['feed_address'] = feed_address

    if is_safe:
        # Build multisend tx
        print(f'Batching {num_to_deploy} deployments')
        hist = history.from_sender(gov.address)
        safe_tx = gov.multisend_from_receipts(hist[-num_to_deploy:])

        # Sign and post
        gov.sign_transaction(safe_tx)
        gov.post_transaction(safe_tx)
    else:
        pass
    # Save addresses to file
    OM.update_all_parameters(all_params, chain_id)
