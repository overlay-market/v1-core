from ape_safe import ApeSafe
from brownie import accounts
from scripts.overlay_management import OM
from scripts.deploy import deploy_feed as df
from scripts.deploy import deploy_market as dm


def main(chain_id):
    OM.connect_to_chain(chain_id)

    print('Getting all parameters')
    all_params = OM.get_all_parameters(chain_id)
    if chain_id == OM.ARB_TEST:
        eoa_name = input('Enter EOA name: ')
        gov = accounts.load(eoa_name)
        is_safe = False
    else:
        gov = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
        is_safe = True

    # Deploy feed and market contracts
    df.main(gov, chain_id, all_params, is_safe)
    dm.main(gov, chain_id, all_params, is_safe)
