import requests
import json
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
    abi = response.json()['result']
    abi = json.loads(abi)

    return abi