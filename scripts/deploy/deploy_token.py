from ape_safe import ApeSafe
import web3
from brownie import accounts, OverlayV1Token
from scripts.overlay_management import OM
from scripts import utils


MINTER_ROLE = web3.solidityKeccak(['string'], ["MINTER"])


def deploy_w_eoa(eoa):
    ovl = eoa.deploy(OverlayV1Token)
    ovl.grantRole(MINTER_ROLE, eoa, {"from": eoa})
    return ovl


def deploy_w_safe(chain_id, safe):
    # Get contract bytecode
    data = OverlayV1Token.bytecode

    # Load create call contract
    create_call = utils.load_const_contract(chain_id, OM.CREATE_CALL)

    # Deploy feed factory and get address
    tx = create_call.performCreate(0, data, {'from': safe.address})
    ovl_address = tx.events['ContractCreation']['newContract']
    return ovl_address


def main(chain_id):
    OM.connect_to_chain(chain_id)
    print('Getting all parameters')
    all_params = OM.get_all_parameters(chain_id)
    if chain_id == OM.ARB_TEST:
        eoa_name = input('Enter EOA name: ')
        eoa = accounts.load(eoa_name)
        ovl = deploy_w_eoa(eoa)
        ovl_addr = ovl.address
    else:
        safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
        ovl_addr = deploy_w_safe(chain_id, all_params, safe)
    print(f'Overlay token deployed at {ovl_addr}')
