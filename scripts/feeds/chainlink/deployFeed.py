from scripts.overlay_management import OM
from brownie import Contract
from scripts import utils


def main(safe, chain_id, all_params):
    """
    Deploys a new OverlayV1ChainlinkFeed contract
    """
    print(f"Commence feed deployment")
    deployable_feeds = OM.get_deployable(chain_id, 'feed')
    if len(deployable_feeds) == 0:
        print('No feeds to deploy')

    for df in deployable_feeds:
        # Get oracle
        oracle = all_params[df]['oracle']

        # Get address of feed factory corresponding to chain and oracle type
        feed_factory_addr =\
            OM.const_addresses[chain_id]['feed_factory'][oracle]
        feed_factory_abi = utils.get_abi(chain_id, feed_factory_addr)

        # Load contract object using feed factory's address and abi
        feed_factory = Contract.from_abi('feed_factory',
                                         feed_factory_addr,
                                         feed_factory_abi)
        
        # Get input parameters for deploying feed
        feed_parameters = list(all_params[df]['feed_parameters'].values())
        
        # Deploy feed and get address of deployed feed from emitted event
        tx = feed_factory.deployFeed(*feed_parameters, {'from': safe.address})
        feed_address = tx.events['FeedDeployed']['feed']
        
        # Sign and post tx
        OM.bundle_sign_post_to_safe(safe)

        # Save address
        all_params[df]['feed_address'] = feed_address
        OM.update_all_parameters(all_params, chain_id)
