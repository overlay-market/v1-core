from brownie import accounts
from scripts.overlay_management import OM
from scripts import utils


def main(eoa, chain_id):
    # TODO: Do this for Safe too
    OM.connect_to_chain(chain_id)
    eoa = accounts.load(eoa)
    ovl = utils.load_const_contract(chain_id, OM.OVL_ADDRESS)
    amount = int(input('Enter amount to mint: '))
    print(f'Minting {amount} OVL to {eoa.address}')
    # Ask are you sure? y/n
    check = input('Are you sure? y/n: ')
    if check == 'y':
        ovl.mint(eoa, amount * 10 ** ovl.decimals(), {"from": eoa})
    else:
        print('Aborting')
        return
