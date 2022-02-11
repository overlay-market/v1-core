import pytest
from brownie import Contract, convert


@pytest.fixture(scope="module")
def gov(accounts):
    '''
    Inputs:
      accounts [Accounts]: List of brownie provided eth account addresses
    Outputs:
      [Account]: Brownie provided eth account address for the Governor Role
    '''
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    '''
    Inputs:
      accounts [Accounts]: List of brownie provided eth account addresses
    Outputs:
      [Account]: Brownie provided eth account address for Alice the trader
    '''
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    '''
    Inputs:
      accounts [Accounts]: List of brownie provided eth account addresses
    Outputs:
      [Account]: Brownie provided eth account address for Bob the trader
    '''
    yield accounts[2]


@pytest.fixture(scope="module")
def rando(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def dai():
    '''
    Outputs:
      [Contract] DAI token contract instance

    https://etherscan.io/address/0x6B175474E89094C44Da98b954EedeAC495271d0F
    '''
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    '''
    Outputs:
      [Contract] WETH token contract instance

    https://etherscan.io/address/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
    '''
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def balancer():
    '''
    Outputs:
      [Contract] Balancer V2 BalancerGovernanceToken token contract instance

    https://etherscan.io/address/0xba100000625a3754423978a60c9317c58a424e3D
    '''
    yield Contract.from_explorer("0xba100000625a3754423978a60c9317c58a424e3D")


@pytest.fixture(scope="module")
def pool_daiweth():
    '''
    Outputs:
      [Contract] Balancer V2 WeightedPool2Tokens contract instance for the
                 DAI/WETH pool


    https://etherscan.io/address/0x0b09deA16768f0799065C475bE02919503cB2a35
    https://app.balancer.fi/#/pool/0x0b09dea16768f0799065c475be02919503cb2a3500020000000000000000001a  # noqa: E501
    '''
    yield Contract.from_explorer("0x0b09deA16768f0799065C475bE02919503cB2a35")


@pytest.fixture(scope="module")
def pool_balweth():
    '''
    Outputs:
      [Contract]: Balancer V2 WeightedPool2Tokens contract instance for the
                  BAL/WETH pool, used as an example OVL/WETH pool

    https://etherscan.io/address/0x5c6ee304399dbdb9c8ef030ab642b10820db8f56
    https://app.balancer.fi/#/pool/0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014  # noqa: E501
    '''
    yield Contract.from_explorer("0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56")


@pytest.fixture(scope="module")
def vault():
    '''
    Outputs:
      [Contract]: BalancerV2Vault contract address as a string to be used as
                  the vault field in the BalancerV2Tokens struct. This struct
                  is an input argument to the OverlayV1BalancerV2Feed
                  constructor

    https://etherscan.io/address/0xBA12222222228d8Ba445958a75a0704d566BF2C8
    '''
    yield Contract.from_explorer('0xBA12222222228d8Ba445958a75a0704d566BF2C8')


@pytest.fixture(scope="module")
def ovl_weth_pool_id():
    '''
    Output:
      [bytes32]: BAL/WETH Balancer V2 pool id
    '''
    yield convert.to_bytes(
        '0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014',
        'bytes32')


@pytest.fixture(scope="module")
def bal_weth_pool_id():
    '''
    Output:
      [bytes32]: DAI/WETH Balancer V2 pool id
    '''
    yield convert.to_bytes(
        '0x0b09dea16768f0799065c475be02919503cb2a3500020000000000000000001a',
        'bytes32')


@pytest.fixture(scope="module")
def dai_usdc_pool_id():
    '''
    Output:
      [bytes32]: DAI/USDC Balancer V2 pool id
    '''
    yield convert.to_bytes(
        '0x06df3b2bbb68adc8b0e302443692037ed9f91b42000000000000000000000063',
        'bytes32')


@pytest.fixture(scope="module")
def balv2_tokens(vault, ovl_weth_pool_id, bal_weth_pool_id):
    '''
    Returns the BalancerV2Vault contract address as a string to be used as the
    vault field in the BalancerV2Tokens struct. This struct is an input
    argument to the OverlayV1BalancerV2Feed constructor.
    https://etherscan.io/address/0xBA12222222228d8Ba445958a75a0704d566BF2C8
    '''
    yield (vault, ovl_weth_pool_id, bal_weth_pool_id)
