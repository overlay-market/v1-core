from eth_abi import encode
from ape_safe import ApeSafe
from scripts.overlay_management import OM
from scripts import utils
from brownie import history, accounts
from web3 import Web3


def get_feed_factory_details(key, all_params):
    ff = all_params[key]
    # Load contract using brownie and get contract object from `locals()`
    exec(f"from brownie import {ff['contract_name']}")
    ff_contract = locals()[ff['contract_name']]
    return ff, ff_contract


def add_feed_factory_to_factory(chain_id, gov, ff_address):
    # Add feed factory to factory
    factory = utils.load_const_contract(chain_id, OM.FACTORY_ADDRESS)
    factory.addFeedFactory(ff_address, {"from": gov})


def deploy_w_safe(chain_id, safe, dep_ff, num, all_params):
    for ff_key in dep_ff:
        print(f'Commencing feed factory deployment: {ff_key}')
        ff, ff_contract = get_feed_factory_details(ff_key, all_params)

        # Encode contract constructor arguments
        ff_params = ff['feed_factory_parameters'].values()
        abi = ff_contract.abi
        args_constructor = abi[0]['inputs']
        types_constructor = [ca['type'] for ca in args_constructor]
        ff_parameters = list(ff_params)
        encoded_constructor = encode(
            types_constructor,
            ff_parameters
        )
        hex_constructor = Web3.toHex(encoded_constructor)[2:]

        # Get contract bytecode and append encoded constructors
        bytecode = ff_contract.bytecode
        data = bytecode + hex_constructor

        # Load create call contract
        create_call = utils.load_const_contract(chain_id, OM.CREATE_CALL)

        # Deploy feed factory and get address
        tx = create_call.performCreate(0, data, {'from': safe.address})
        ff_address = tx.events['ContractCreation']['newContract']

        # Save address to dict
        all_params[ff_key]['feed_factory_address'] = ff_address

        # Save verification info (for etherscan verification)
        ff_params_str = '_'.join(str(param) for param in ff_params)
        OM.get_verification_info(
            ff_contract, f"{ff['contract_name']}_{ff_params_str}"
        )

        # Add feed factory to factory
        add_feed_factory_to_factory(chain_id, safe.address, ff_address)

    # Build multisend tx
    # Two txs per feed factory: 1) Deployment; 2) Addition to factory
    print(f'Batching {num*2} transactions')
    hist = history.from_sender(safe.address)
    safe_tx = safe.multisend_from_receipts(hist[-num*2:])

    # Sign and post
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)

    return all_params


def deploy_w_eoa(chain_id, eoa, dep_ff, all_params):
    for ff_key in dep_ff:
        print(f'Commencing feed factory deployment: {ff_key}')
        ff, ff_contract = get_feed_factory_details(ff_key, all_params)
        # Deploy feed factory and get address
        ff_params = ff['feed_factory_parameters'].values()
        eoa.deploy(ff_contract, *ff_params)
        ff_address = ff_contract[-1].address
        # Save verification info (for etherscan verification)
        ff_params_str = '_'.join(str(param) for param in ff_params)
        OM.get_verification_info(
            ff_contract, f"{ff['contract_name']}_{ff_params_str}"
        )
        # Save address to dict
        all_params[ff_key]['feed_factory_address'] = ff_address
        # Add feed factory to factory
        add_feed_factory_to_factory(chain_id, eoa.address, ff_address)
    return all_params


def main(chain_id):
    """
    Deploys a new Feed Factory contract
    """
    print("Commence feed factory deployment script")
    OM.connect_to_chain(chain_id)
    all_params = OM.get_all_parameters(chain_id)
    deployable_ff = OM.get_deployable_feed_factory(chain_id)
    num_to_deploy = len(deployable_ff)
    if num_to_deploy == 0:
        return
    print(f'Feed factories to deploy: {num_to_deploy}')
    if chain_id == OM.ARB_TEST:
        eoa_name = input('Enter EOA name: ')
        eoa = accounts.load(eoa_name)
        all_params = deploy_w_eoa(chain_id, eoa, deployable_ff, all_params)
    else:
        safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
        all_params = deploy_w_safe(
            chain_id, safe, deployable_ff,
            num_to_deploy, all_params
        )

    # Save addresses to file
    OM.update_all_parameters(all_params, chain_id)
