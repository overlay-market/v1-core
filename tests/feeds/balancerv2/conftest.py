import pytest
from brownie import Contract, convert, OverlayV1BalancerV2Feed


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
    '''
    Inputs:
      accounts [Accounts]: List of brownie provided eth account addresses
    Outputs:
      [Account]: Brownie provided eth account address for a random account
    '''
    yield accounts[3]


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
def balancer():
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


@pytest.fixture(scope="module")
def pool_parusdc():
    '''

    Outputs:
      [Contract] Balancer V2 WeightedPool2Tokens contract instance for the
                 PAR/USDC pool


    https://etherscan.io/address/0x5d6e3d7632D6719e04cA162be652164Bec1EaA6b
    https://app.balancer.fi/#/pool/0x5d6e3d7632d6719e04ca162be652164bec1eaa6b000200000000000000000048  # noqa: E501
    '''
    yield Contract.from_explorer("0x5d6e3d7632D6719e04cA162be652164Bec1EaA6b")


@pytest.fixture(scope="module")
def balweth_poolid():
    '''
    Output:
      [bytes32]: DAI/WETH Balancer V2 OracleWeightedPool contract pool id
    '''
    yield convert.to_bytes(
        '0x0b09dea16768f0799065c475be02919503cb2a3500020000000000000000001a',
        'bytes32')


@pytest.fixture(scope="module")
def parusdc_poolid():
    '''
    This pool is used for testing the require statements in the
    OverlayV1BalancerV2Feed contract constructor function.

    Output:
      [bytes32]: PAR/USDC Balancer V2 OracleWeightedPool contract pool id
    '''
    yield convert.to_bytes(
        '0x5d6e3d7632d6719e04ca162be652164bec1eaa6b000200000000000000000048',
        'bytes32')


@pytest.fixture(scope="module")
def balv2_tokens(balweth_poolid):
    '''
    Returns the BalancerV2Tokens struct fields for a DAI/WETH market token pair
    using the BAL/WETH token pair to simulate the OVL/WETH token pair for
    testing. The BalancerV2Tokens struct is an input argument to the
    constructor of the OverlayV1BalancerV2Feed contract so that token addresses
    can be retrieved from the BalancerV2 Vault contract.

    Inputs:
      balweth_poolid [bytes32]: DAI/WETH Balancer V2 OracleWeightedPool
                                contract pool id, representing the market token
                                pair
    Outputs:
      (
         [Contract]: BalancerV2Vault contract instance
         [bytes32]:  BAL/WETH Balancer V2 OracleWeighted contract pool id,
                     representing the OVL/WETH token pair
         [bytes32]:  DAI/WETH Balancer V2 OracleWeightedPool contract pool id,
                     representing the market token pair
      )
    '''
    # BalancerV2Vault contract address is BalancerV2Tokens.vault
    # https://etherscan.io/address/0xBA12222222228d8Ba445958a75a0704d566BF2C8
    vault = Contract.from_explorer(
            '0xBA12222222228d8Ba445958a75a0704d566BF2C8')

    ovlweth_poolid = convert.to_bytes(
        '0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014',
        'bytes32')
    yield (vault, ovlweth_poolid, balweth_poolid)


@pytest.fixture(scope="module")
def feed(gov, balancer, weth, dai, balv2_tokens, pool_daiweth, pool_balweth):
    '''
    Successfully deploys the OverlayV1BalancerV2Feed contract for a DAI/WETH
    market pool. The OVL/WETH pool is simulated using the BAL/WETH pool.

    Inputs:
      gov          [Account]:  Governor role account deploys the
                               OverlayV1BalancerV2Feed contract
      dai          [Contract]: DAI token contract instance
      weth         [Contract]: WETH token contract instance
      balancer     [Contract]: BAL token contract instance representing the OVL
                               token
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
      pool_daiweth [Contract]: Balancer V2 WeightedPool2Tokens contract
                               instance for the DAI/WETH pool
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
    '''
    market_pool = pool_daiweth
    ovlweth_pool = pool_balweth
    ovl = balancer
    market_base_token = weth
    market_quote_token = dai
    market_base_amount = 1 * 10 ** weth.decimals()

    balv2_pool = (market_pool, ovlweth_pool, ovl, market_base_token,
                  market_quote_token,  market_base_amount)

    micro_window = 600
    macro_window = 3600

    yield gov.deploy(OverlayV1BalancerV2Feed, balv2_pool, balv2_tokens,
                     micro_window, macro_window)
