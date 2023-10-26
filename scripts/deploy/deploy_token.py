from ape_safe import ApeSafe
from brownie import network, accounts
from scripts.overlay_management import OM


def main(chain_id):
    OM.connect_to_chain(chain_id)
    print('Getting all parameters')
    all_params = OM.get_all_parameters(chain_id)
    if chain_id == OM.ARB_TEST:
        eoa_name = input('Enter EOA name: ')
        # EOA will be called safe for consistency
        safe = accounts.load(eoa_name)
    else:
        safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])

