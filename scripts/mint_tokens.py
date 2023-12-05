from brownie import accounts
from scripts.overlay_management import OM
from scripts import utils
from brownie import web3


def main(eoa, chain_id):
    # TODO: Do this for Safe too
    OM.connect_to_chain(chain_id)
    eoa = accounts.load(eoa)
    ovl = utils.load_const_contract(chain_id, OM.OVL_ADDRESS)
    amount = int(input('Enter amount to mint: '))
    to_address = input('Enter address to mint to (leave blank if mint to gov): ')  # noqa: E501
    if to_address == '':
        to_address = eoa.address
    print(f'Minting {amount} OVL to {to_address}')
    # Ask are you sure? y/n
    check = input('Are you sure? y/n: ')
    if check == 'y':
        minter_role = web3.keccak(text='MINTER')
        ovl.grantRole(minter_role, eoa, {"from": eoa})
        ovl.mint(to_address, amount * 10 ** ovl.decimals(), {"from": eoa})
    else:
        print('Aborting')
        return
