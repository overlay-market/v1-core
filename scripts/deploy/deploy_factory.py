from ape_safe import ApeSafe
from brownie import accounts, OverlayV1Factory, Contract, history, web3
from scripts.overlay_management import OM
from scripts import utils


MINTER_ROLE = web3.solidityKeccak(['string'], ["MINTER"])


def deploy_w_eoa(eoa, ovl, recipient_addr):
    # Deploy Factory
    fac = eoa.deploy(OverlayV1Factory, ovl.address, recipient_addr)
    # Grant admin role to Factory
    ovl.grantRole(ovl.DEFAULT_ADMIN_ROLE(), fac, {"from": eoa})
    return fac


def main(chain_id):
    OM.connect_to_chain(chain_id)
    ovl = utils.load_const_contract(chain_id, OM.OVL_ADDRESS)
    if chain_id == OM.ARB_TEST:
        eoa_name = input('Enter EOA name: ')
        eoa = accounts.load(eoa_name)
        # Note: Fee recipient is the gov EOA on arbitrum testnet
        factory = deploy_w_eoa(eoa, ovl, eoa.address)
        factory_addr = factory.address
    # else:
    #     safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
    #     factory_addr = deploy_w_safe(chain_id, safe)
    print(f'OverlayV1Factory deployed at {factory_addr}')
    OM.get_verification_info(OverlayV1Factory, 'OverlayV1Factory')
