from brownie import accounts, network
from scripts.overlay_management import OM
from scripts.feeds.chainlink import deployFeed as df
from scripts.feeds.chainlink import deployMarket as dm


def main(acc_addr, chain_id):
    print(f"You are using the '{network.show_active()}' network")

    print('Getting all parameters')
    all_params = OM.get_all_parameters(chain_id)
    acc = accounts.load(acc_addr)

    # Deploy feed and market contracts
    df.main(acc, chain_id, all_params)
    dm.main(acc, chain_id, all_params)
