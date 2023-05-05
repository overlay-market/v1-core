from eth_abi import encode
from ape_safe import ApeSafe
from scripts.overlay_management import OM
from scripts import utils
from brownie import history
import json
from web3 import Web3


def main(chain_id):
    """
    Deploys a new Feed Factory contract
    """
    print("Commence feed factory deployment script")
    safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
    all_params = OM.get_all_parameters(chain_id)
    deployable_ff = OM.get_deployable_feed_factory(chain_id)
    num_to_deploy = len(deployable_ff)
    print(f'Feed factories to deploy: {num_to_deploy}')
    if num_to_deploy == 0:
        return

    for ff_key in deployable_ff:
        print(f'Commencing feed factory deployment: {ff_key}')
        ff = all_params[ff_key]

        # Load contract using brownie and get contract object from `locals()`
        exec(f"from brownie import {ff['contract_name']}")
        ff_contract = locals()[ff['contract_name']]

        # Encode contract constructor arguments
        abi = ff_contract.abi
        args_constructor = abi[0]['inputs']
        types_constructor = [ca['type'] for ca in args_constructor]
        ff_parameters = list(ff['feed_factory_parameters'].values())
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
        verif_info = ff_contract.get_verification_info()
        verif_info['abi_encoded_constructor_arguments'] = hex_constructor
        ff_parameters_str = '_'.join(str(ffp) for ffp in ff_parameters)
        file_name = f"{ff['contract_name']}_{chain_id}_{ff_parameters_str}"
        with open(f'scripts/deploy/{file_name}.json', 'w') as j:
            json.dump(verif_info, j, indent=4)

        # Add feed factory to factory
        factory = utils.load_const_contract(chain_id, OM.FACTORY_ADDRESS)
        factory.addFeedFactory(ff_address, {"from": safe.address})

    # Build multisend tx
    # Two txs per feed factory: 1) Deployment; 2) Addition to factory
    print(f'Batching {num_to_deploy*2} transactions')
    hist = history.from_sender(safe.address)
    safe_tx = safe.multisend_from_receipts(hist[-num_to_deploy*2:])

    # Sign and post
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)

    # Save addresses to file
    OM.update_all_parameters(all_params, chain_id)
