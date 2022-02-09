import pytest
from brownie import Contract, OverlayV1BalancerV2Feed, convert


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
    Returns the DAI token contract instance used to simulate OVL for testing
    purposes.

    https://etherscan.io/address/0x6B175474E89094C44Da98b954EedeAC495271d0F
    '''
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    '''
    Returns the WETH token contract instance.

    https://etherscan.io/address/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
    '''
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def balancer():
    '''
    Returns the Balancer V2 BalancerGovernanceToken contract instance.

    https://etherscan.io/address/0xba100000625a3754423978a60c9317c58a424e3D
    '''
    yield Contract.from_explorer("0xba100000625a3754423978a60c9317c58a424e3D")


@pytest.fixture(scope="module")
def pool_daiweth():
    '''
    Returns the BalancerV2 WeightedPool2Tokens contract instance for the
    DAI/WETH pool.

    https://etherscan.io/address/0x0b09deA16768f0799065C475bE02919503cB2a35
    https://app.balancer.fi/#/pool/0x0b09dea16768f0799065c475be02919503cb2a3500020000000000000000001a  # noqa: E501
    '''
    yield Contract.from_explorer("0x0b09deA16768f0799065C475bE02919503cB2a35")


@pytest.fixture(scope="module")
def pool_balweth():
    '''
    Returns the BalancerV2 WeightedPool2Tokens contract instance for the
    BAL/WETH pool. Intended to be used as an example OVL/WETH pool.

    https://etherscan.io/address/0x5c6ee304399dbdb9c8ef030ab642b10820db8f56
    https://app.balancer.fi/#/pool/0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014  # noqa: E501
    '''
    yield Contract.from_explorer("0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56")


@pytest.fixture(scope="module")
def vault():
    '''
    Returns the BalancerV2Vault contract address as a string to be used as the
    vault field in the BalancerV2Tokens struct. This struct is an input
    argument to the OverlayV1BalancerV2Feed constructor.

    https://etherscan.io/address/0xBA12222222228d8Ba445958a75a0704d566BF2C8
    '''
    yield "0xBA12222222228d8Ba445958a75a0704d566BF2C8"


@pytest.fixture(scope="module")
def balv2_tokens():
    '''
    Returns the BalancerV2Vault contract address as a string to be used as the
    vault field in the BalancerV2Tokens struct. This struct is an input
    argument to the OverlayV1BalancerV2Feed constructor.

    https://etherscan.io/address/0xBA12222222228d8Ba445958a75a0704d566BF2C8
    '''
    vault = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
    ovl_weth_pool_id = convert.to_bytes(
        '0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014',
        'bytes32')
    bal_weth_pool_id = convert.to_bytes(
        '0x0b09dea16768f0799065c475be02919503cb2a3500020000000000000000001a',
        'bytes32')
    yield (vault, ovl_weth_pool_id, bal_weth_pool_id)


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_quanto_feed(gov, pool_daiweth, pool_balweth,
                       dai, weth, uni, request):
    micro, macro = request.param

    mkt_pool = pool_daiweth.address
    oe_pool = pool_balweth.address
    tok = uni.address
    mkt_base_tok = weth.address
    mkt_quote_tok = dai.address
    mkt_base_amt = 1 * 10 ** weth.decimals()

    def create_quanto_feed(market_pool=mkt_pool, ovlweth_pool=oe_pool, ovl=tok,
                           market_base_token=mkt_base_tok,
                           market_quote_token=mkt_quote_tok,
                           market_base_amount=mkt_base_amt, micro_window=micro,
                           macro_window=macro):
        feed = gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool,
                          ovl, market_base_token, market_quote_token,
                          market_base_amount, micro_window, macro_window)
        return feed

    yield create_quanto_feed


@pytest.fixture(scope="module")
def quanto_feed(create_quanto_feed):
    yield create_quanto_feed()


@pytest.fixture(scope="module", params=[(600, 3600)])
def create_inverse_feed(gov, pool_balweth, weth, uni, request):
    micro, macro = request.param

    # treating uni as ovl for testing
    mkt_pool = pool_balweth.address
    oe_pool = pool_balweth.address
    tok = uni.address
    mkt_base_tok = weth.address
    mkt_quote_tok = uni.address
    mkt_base_amt = 1 * 10 ** uni.decimals()

    def create_inverse_feed(market_pool=mkt_pool, ovlweth_pool=oe_pool,
                            ovl=tok, market_base_token=mkt_base_tok,
                            market_quote_token=mkt_quote_tok,
                            market_base_amount=mkt_base_amt,
                            micro_window=micro, macro_window=macro):
        feed = gov.deploy(OverlayV1BalancerV2Feed, market_pool, ovlweth_pool,
                          ovl, market_base_token, market_quote_token,
                          market_base_amount, micro_window, macro_window)
        return feed

    yield create_inverse_feed


@pytest.fixture(scope="module")
def inverse_feed(create_inverse_feed):
    yield create_inverse_feed()
