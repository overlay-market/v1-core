import pytest
from brownie import (
    Contract, OverlayV1Token, OverlayV1Market, OverlayV1Factory,
    OverlayV1UniswapV3Factory, OverlayV1FeedFactoryMock,
    OverlayV1FeedMock, OverlayV1Deployer, OverlayV1UniswapV3Feed, web3
)


@pytest.fixture(scope="module")
def gov(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def rando(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def fee_recipient(accounts):
    yield accounts[4]


@pytest.fixture(scope="module")
def fake_factory(accounts):
    yield accounts[5]


@pytest.fixture(scope="module")
def guardian(accounts):
    yield accounts[6]


@pytest.fixture(scope="module")
def minter_role():
    yield web3.solidityKeccak(['string'], ["MINTER"])


@pytest.fixture(scope="module")
def burner_role():
    yield web3.solidityKeccak(['string'], ["BURNER"])


@pytest.fixture(scope="module")
def governor_role():
    yield web3.solidityKeccak(['string'], ["GOVERNOR"])


@pytest.fixture(scope="module")
def guardian_role():
    yield web3.solidityKeccak(['string'], ["GUARDIAN"])


@pytest.fixture(scope="module", params=[8000000])
def create_token(gov, alice, bob, minter_role, request):
    sup = request.param

    def create_token(supply=sup):
        tok = gov.deploy(OverlayV1Token)

        # mint the token then renounce minter role
        tok.grantRole(minter_role, gov, {"from": gov})
        tok.mint(gov, supply * 10 ** tok.decimals(), {"from": gov})
        tok.renounceRole(minter_role, gov, {"from": gov})

        tok.transfer(alice, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        tok.transfer(bob, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        return tok

    yield create_token


@pytest.fixture(scope="module")
def ovl(create_token):
    yield create_token()


@pytest.fixture(scope="module", params=[
    (600, 1800, 1000000000000000000, 2000000000000000000000000)
])
def create_fake_feed(gov, request):
    micro, macro, p, r = request.param

    def create_fake_feed(micro_window=micro, macro_window=macro,
                         price=p, reserve=r):
        fake_feed = gov.deploy(OverlayV1FeedMock, micro_window, macro_window,
                               price, reserve)
        return fake_feed

    yield create_fake_feed


@pytest.fixture(scope="module")
def fake_feed(create_fake_feed):
    yield create_fake_feed()


@pytest.fixture(scope="module")
def dai():
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def uni():
    # to be used as example ovl
    yield Contract.from_explorer("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")


@pytest.fixture(scope="module")
def uni_factory():
    yield Contract.from_explorer("0x1F98431c8aD98523631AE4a59f267346ea31F984")


@pytest.fixture(scope="module")
def pool_daiweth_30bps():
    yield Contract.from_explorer("0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")


@pytest.fixture(scope="module")
def pool_uniweth_30bps():
    # to be used as example ovlweth pool
    yield Contract.from_explorer("0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801")


# TODO: change params to (600, 3600, 300, 14)
@pytest.fixture(scope="module", params=[(600, 1800, 240, 15)])
def create_feed_factory(gov, uni_factory, weth, uni, request):
    micro, macro, cardinality, block_time = request.param
    tok = uni.address
    uni_fact = uni_factory

    def create_feed_factory(univ3_factory=uni_fact, ovl=tok,
                            micro_window=micro, macro_window=macro,
                            cardinality_min=cardinality,
                            avg_block_time=block_time):
        feed_factory = gov.deploy(OverlayV1UniswapV3Factory, ovl,
                                  univ3_factory, micro_window, macro_window,
                                  cardinality_min, avg_block_time)
        return feed_factory

    yield create_feed_factory


@pytest.fixture(scope="module")
def feed_factory(create_feed_factory):
    yield create_feed_factory()


# TODO: params for different OverlayV1Feed types ... (to test BalancerV2
# and UniswapV3 in same test run)
@pytest.fixture(scope="module")
def create_feed(gov, feed_factory, pool_daiweth_30bps, pool_uniweth_30bps,
                uni, dai, weth, request):
    # ovlweth treated as uniweth for test purposes, feed ovl treated as uni
    mkt_fee = pool_daiweth_30bps.fee()
    mkt_base_tok = weth.address
    mkt_quote_tok = dai.address
    mkt_base_amt = 1 * 10 ** weth.decimals()

    ovlweth_base_tok = weth.address
    ovlweth_quote_tok = uni.address
    ovlweth_fee = pool_uniweth_30bps.fee()

    def create_feed(market_base_token=mkt_base_tok,
                    market_quote_token=mkt_quote_tok,
                    market_fee=mkt_fee,
                    market_base_amount=mkt_base_amt,
                    ovlx_base_token=ovlweth_base_tok,
                    ovlx_quote_token=ovlweth_quote_tok,
                    ovlx_fee=ovlweth_fee):
        tx = feed_factory.deployFeed(
            market_base_token, market_quote_token, market_fee,
            market_base_amount, ovlx_base_token, ovlx_quote_token, ovlx_fee)
        feed_addr = tx.return_value
        feed = OverlayV1UniswapV3Feed.at(feed_addr)
        return feed

    yield create_feed


@pytest.fixture(scope="module")
def feed(create_feed):
    yield create_feed()


@pytest.fixture(scope="module", params=[(600, 1800)])
def create_mock_feed_factory(gov, request):
    micro, macro = request.param

    def create_mock_feed_factory(micro_window=micro, macro_window=macro):
        feed_factory = gov.deploy(OverlayV1FeedFactoryMock, micro_window,
                                  macro_window)
        return feed_factory

    yield create_mock_feed_factory


@pytest.fixture(scope="module")
def mock_feed_factory(create_mock_feed_factory):
    yield create_mock_feed_factory()


# Mock feed to easily change price/reserve for testing of various conditions
@pytest.fixture(scope="module", params=[
    (1000000000000000000, 2000000000000000000000000)
])
def create_mock_feed(gov, mock_feed_factory, request):
    price, reserve = request.param

    def create_mock_feed(price=price, reserve=reserve):
        tx = mock_feed_factory.deployFeed(price, reserve)
        mock_feed_addr = tx.return_value
        mock_feed = OverlayV1FeedMock.at(mock_feed_addr)
        return mock_feed

    yield create_mock_feed


@pytest.fixture(scope="module")
def mock_feed(create_mock_feed):
    yield create_mock_feed()


@pytest.fixture(scope="module")
def create_factory(gov, guardian, fee_recipient, request, ovl, governor_role,
                   guardian_role, feed_factory, mock_feed_factory):
    def create_factory(tok=ovl, recipient=fee_recipient):
        # create the market factory
        factory = gov.deploy(OverlayV1Factory, tok, recipient)

        # grant market factory token admin role
        tok.grantRole(tok.DEFAULT_ADMIN_ROLE(), factory, {"from": gov})

        # grant gov the governor role on token to access factory methods
        tok.grantRole(governor_role, gov, {"from": gov})
        # grant gov the guardian role on token to access factory methods
        tok.grantRole(guardian_role, guardian, {"from": gov})

        # add both feed factories
        factory.addFeedFactory(feed_factory, {"from": gov})
        factory.addFeedFactory(mock_feed_factory, {"from": gov})

        return factory
    yield create_factory


@pytest.fixture(scope="module")
def factory(create_factory):
    yield create_factory()


@pytest.fixture(scope="module")
def create_fake_deployer(fake_factory, ovl):
    def create_fake_deployer(fake_factory=fake_factory, ovl=ovl):
        return fake_factory.deploy(OverlayV1Deployer, ovl)

    yield create_fake_deployer


@pytest.fixture(scope="module")
def fake_deployer(create_fake_deployer):
    yield create_fake_deployer()


@pytest.fixture(scope="module")
def create_market(gov, ovl):
    def create_market(feed, factory, feed_factory, risk_params,
                      governance=gov, ovl=ovl):
        tx = factory.deployMarket(
            feed_factory, feed, risk_params, {"from": gov})
        market_addr = tx.return_value
        market = OverlayV1Market.at(market_addr)
        return market

    yield create_market


@pytest.fixture(scope="module", params=[(
    122000000000,  # k
    500000000000000000,  # lmbda
    2500000000000000,  # delta
    5000000000000000000,  # capPayoff
    800000000000000000000000,  # capNotional
    5000000000000000000,  # capLeverage
    2592000,  # circuitBreakerWindow
    66670000000000000000000,  # circuitBreakerMintTarget
    100000000000000000,  # maintenanceMargin
    100000000000000000,  # maintenanceMarginBurnRate
    50000000000000000,  # liquidationFeeRate
    750000000000000,  # tradingFeeRate
    100000000000000,  # minCollateral
    25000000000000,  # priceDriftUpperLimit
    14,  # averageBlockTime
)])
def mock_market(gov, mock_feed, mock_feed_factory, factory, ovl,
                create_market, request):
    risk_params = request.param
    yield create_market(feed=mock_feed, feed_factory=mock_feed_factory,
                        factory=factory, risk_params=risk_params,
                        governance=gov, ovl=ovl)


@pytest.fixture(scope="module", params=[(
    122000000000,  # k
    500000000000000000,  # lmbda
    2500000000000000,  # delta
    5000000000000000000,  # capPayoff
    800000000000000000000000,  # capNotional
    5000000000000000000,  # capLeverage
    2592000,  # circuitBreakerWindow
    66670000000000000000000,  # circuitBreakerMintTarget
    100000000000000000,  # maintenanceMarginFraction
    100000000000000000,  # maintenanceMarginBurnRate
    50000000000000000,  # liquidationFeeRate
    750000000000000,  # tradingFeeRate
    100000000000000,  # minCollateral
    25000000000000,  # priceDriftUpperLimit
    14,  # averageBlockTime
)])
def market(gov, feed, feed_factory, factory, ovl, create_market, request):
    risk_params = request.param
    yield create_market(feed=feed, feed_factory=feed_factory,
                        factory=factory, risk_params=risk_params,
                        governance=gov, ovl=ovl)
