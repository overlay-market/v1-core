from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.overlay_management import OM
from scripts.deploy import deploy_feed as df
from scripts.deploy import deploy_market as dm


def main(chain_id):
    print(f"You are using the '{network.show_active()}' network")

    print('Getting all parameters')
    all_params = OM.get_all_parameters(chain_id)
    safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])

    # Deploy feed and market contracts
    df.main(safe, chain_id, all_params)
    dm.main(safe, chain_id, all_params)
