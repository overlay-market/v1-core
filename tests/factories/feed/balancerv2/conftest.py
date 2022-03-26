import pytest
from brownie import Contract, OverlayV1BalancerV2Factory


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
def dai():
    '''
    Outputs:
      [Contract]: DAI token contract instance

    https://etherscan.io/address/0x6B175474E89094C44Da98b954EedeAC495271d0F
    '''
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    '''
    Outputs:
      [Contract]: WETH token contract instance

    https://etherscan.io/address/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
    '''
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def bal():
    '''
    Outputs:
      [Contract]: BalancerGovernanceToken token contract instance

    https://etherscan.io/address/0xba100000625a3754423978a60c9317c58a424e3D
    '''
    yield Contract.from_explorer("0xba100000625a3754423978a60c9317c58a424e3D")


@pytest.fixture(scope="module")
def pool_daiweth():
    '''
    Outputs:
      [Contract]: Balancer V2 WeightedPool2Tokens contract instance for the
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
                  BAL/WETH pool, used as an example OVL/WETH pair.

    https://etherscan.io/address/0x5c6ee304399dbdb9c8ef030ab642b10820db8f56
    https://app.balancer.fi/#/pool/0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014  # noqa: E501
    '''
    yield Contract.from_explorer("0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56")


@pytest.fixture(scope="module", params=[(600, 3600)])
def factory(gov, weth, bal, pool_balweth, request):
    '''
    Successfully deploys the OverlayV1BalancerV2Feed contract for a DAI/WETH
    market pool. The OVL/WETH pool is simulated using the BAL/WETH pool.

    Inputs:
      gov          [Account]:  Governor role account deploys the
                               OverlayV1BalancerV2Feed contract
      weth         [Contract]: WETH token contract instance
      bal          [Contract]: BAL token contract instance representing the OVL
                               token
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
      request      [dict]:     Params specified in fixture
                   [int]:      Micro window, 600 seconds
                   [int]:      Macro window, 3600 seconds
    '''
    micro_window, macro_window = request.param
    ovl = bal.address

    return gov.deploy(OverlayV1BalancerV2Factory, pool_balweth.address, ovl,
                      micro_window, macro_window)
