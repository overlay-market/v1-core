import requests
import json
from brownie import Contract
import time
from scripts.overlay_management import OM


def get_abi(chain_id, address):
    if chain_id == OM.ARB_TEST:
        api = 'api-goerli.arbiscan'
    elif chain_id == OM.ETH_MAIN:
        api = 'api.etherscan'
    elif chain_id == OM.ARB_MAIN:
        api = 'api.arbiscan'
    elif chain_id == OM.ETH_TEST:
        api = 'api-goerli.etherscan'

    url = f'https://{api}.io/api?module=contract&action=getabi&address={address}'

    response = requests.get(url)
    time.sleep(3)  # To avoid rate limit
    abi = response.json()['result']
    abi = json.loads(abi)

    return abi


def load_const_contract(chain_id, contract_name):
    contract_addr = OM.const_addresses[chain_id][contract_name]
    return load_contract(chain_id, contract_addr, contract_name)


def load_contract(chain_id, contract_addr, contract_name='contract'):
    try:
        return Contract(contract_addr)
    except ValueError:
        contract_abi = get_abi(chain_id, contract_addr)
        return Contract.from_abi(contract_name, contract_addr, contract_abi)