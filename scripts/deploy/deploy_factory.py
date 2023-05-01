from eth_utils import keccak
from eth_abi import encode
from ape_safe import ApeSafe
from scripts.overlay_management import OM
from scripts import utils
from brownie import (
    Contract, history,
    accounts, network
)
import json
from web3 import Web3

def main(chain_id):
    # TODO: This is deprecated and needs to be redone completely
    """
    Deploys a new Feed Factory contract
    """
    safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
    deployable_ff = OM.get_deployable_feed_factory(chain_id)
    
    for ff in deployable_ff:
        # Load the contract using brownie and get contract object from `locals()`
        exec(f"from brownie import {ff['contract_name']}")
        ff_contract = locals()[ff['contract_name']]
        # Encode contract constructor arguments
        abi = ff_contract.abi
        args_constructor = abi[0]['inputs']
        types_constructor = [ca['type'] for ca in args_constructor]
        encoded_constructor = encode(
            types_constructor,
            list(ff['feed_factory_parameters'].values())
        )
        hex_constructor = Web3.toHex(encoded_constructor)[2:]
        # Get contract bytecode and append encoded constructors
        bytecode = ff_contract.bytecode
        data = bytecode + hex_constructor