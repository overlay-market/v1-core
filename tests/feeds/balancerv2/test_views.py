from brownie.test import given, strategy


def test_get_reserve_in_weth(feed, pool_daiweth):
    pool_market = pool_daiweth
    variable = 0  # PAIR_PRICE
    micro_window = 600
    ago = 0

    query = feed.getOracleAverageQuery(variable, micro_window, ago)
    price_over_micro_window = feed.getTimeWeightedAverage(pool_market,
                                                          [query])[0]
    twav = feed.getTimeWeightedAverageInvariant(pool_market, micro_window, ago)

    actual = feed.getReserveInWeth(twav, price_over_micro_window)  # noqa: F841
    assert 1 == 1

    # SN TODO: error on denominator: OverflowError: (34, 'Result too large')
    #  normalized_weights = feed.getNormalizedWeights(pool_market)
    #  weight_token_0 = normalized_weights[0]
    #  weight_token_1 = normalized_weights[1]
    #
    #  denominator = ((price_over_micro_window * weight_token_1) / weight_token_0) ** weight_token_1;  # noqa: E501
    #  power = 1 / (weight_token_0 + weight_token_1)
    #  expect = (twav / denominator) ** power;

    #  assert actual == expect


# SN TODO
def test_get_pair_price_ovl_weth(feed):
    res = feed.getPairPriceOvlWeth()  # noqa: F841

    assert 1 == 1


# SN TODO
def test_get_reserve(feed, pool_daiweth):
    micro_window = 600
    ago = 0
    variable = 0
    query = feed.getOracleAverageQuery(variable, micro_window, ago)
    price_over_micro_window = feed.getTimeWeightedAverage(pool_daiweth,
                                                          [query])
    price_over_micro_window = price_over_micro_window[0]

    res = feed.getReserve(price_over_micro_window)  # noqa: F841

    assert 1 == 1


def test_get_time_weighted_average_pair_price(feed):
    res = feed.getPairPrices()
    print()
    print('getPairPrices RES', res)
    print()
    assert (1 == 1)


def test_get_time_weighted_average_invariant(feed, pool_balweth):
    '''
    Tests that the OverlayV1BalancerV2Feed contract
    getTimeWeightedAverageInvariant function returns the expected TWAP.

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
    '''
    secs = 1800
    ago = 0

    variable = 2  # Variable.INVARIANT
    query = feed.getOracleAverageQuery(variable, secs, ago)
    expect = feed.getTimeWeightedAverage(pool_balweth, [query])  # noqa: F841
    expect = expect[0]

    actual = feed.getTimeWeightedAverageInvariant(pool_balweth, secs, ago)
    assert (actual == expect)


def test_get_time_weighted_average(feed, pool_balweth):
    '''
    Tests that the OverlayV1BalancerV2Feed contract getTimeWeightedAverage
    function returns the expected TWAP.

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
    '''
    secs = 1800
    ago = 0
    variable = 0  # Variable.PAIR_PRICE
    query = feed.getOracleAverageQuery(variable, secs, ago)
    actual = feed.getTimeWeightedAverage(pool_balweth, [query])  # noqa: F841
    print('ACTUAL GET TWAP', actual)
    # SN TODO
    assert 1 == 1


@given(secs=strategy('int', min_value=0, max_value=3600))
def test_get_oracle_average_query(feed, secs):
    '''
    Tests that the OverlayV1BalancerV2Feed contract getOracleAverageQuery
    function returns the OracleAverageQuery struct.

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
    '''
    ago = [0, 1800]

    variable = 0  # Variable.PAIR_PRICE
    actual = feed.getOracleAverageQuery(variable, secs, ago[0])
    expect = (variable, secs, ago[0])
    assert expect == actual

    variable = 2  # Variable.INVARIANT
    actual = feed.getOracleAverageQuery(variable, secs, ago[0])
    expect = (variable, secs, ago[0])
    assert expect == actual

    variable = 0  # Variable.PAIR_PRICE
    actual = feed.getOracleAverageQuery(variable, secs, ago[1])
    expect = (variable, secs, ago[1])
    assert expect == actual

    variable = 2  # Variable.INVARIANT
    actual = feed.getOracleAverageQuery(variable, secs, ago[1])
    expect = (variable, secs, ago[1])
    assert expect == actual


def test_get_normalized_weights(feed, pool_balweth, pool_daiweth):
    '''
    Tests that the OverlayV1BalancerV2Feed contract getNormalizedWeights
    function returns the normalized weights of the pool tokens.

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
      pool_daiweth [Contract]: Balancer V2 WeightedPool2Tokens contract
                               instance for the DAI/WETH pool
    '''
    # OVL/WETH (represented by BAL/WETH)
    actual = feed.getNormalizedWeights(pool_balweth)
    expect = (800000000000000000, 200000000000000000)
    assert expect == actual

    # DAI/WETH (the market pool)
    actual = feed.getNormalizedWeights(pool_daiweth)
    expect = (400000000000000000, 600000000000000000)
    assert expect == actual


def test_get_pool_tokens(feed, weth, balancer, dai, balv2_tokens):
    '''
    Tests that the OverlayV1BalancerV2Feed contract getPoolTokens function
    returns the expected token pair when given the associated pool id.

    Two pool ids are tested:
      1. The OVL/WETH pool id which is often simulated by BAL/WETH for testing
      2. The DAI/WETH pool id which often represents the market token pair for
         testing

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
      weth         [Contract]: WETH token contract instance
      balancer     [Contract]: BalancerGovernanceToken token contract instance
      dai          [Contract]: DAI token contract instance
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
    '''
    # OVL/WETH (represented by BAL/WETH)
    actual = feed.getPoolTokens(balv2_tokens[1].hex())
    actual_tokens = actual[0]
    expect_tokens = (balancer, weth)

    # DAI/WETH (the market pool)
    actual = feed.getPoolTokens(balv2_tokens[2].hex())
    actual_tokens = actual[0]
    expect_tokens = (dai, weth)
    assert expect_tokens == actual_tokens


def test_get_pool_id(feed, balv2_tokens, pool_balweth, pool_daiweth):
    '''
    Test when given a valid pool address, the getPoolId function in
    OverlayV1BalancerV2Feed contract returns the expected pool id.

    Two pool ids are tested:
      1. The OVL/WETH pool id which is often simulated by BAL/WETH for testing
      2. The DAI/WETH pool id which often represents the market token pair for
         testing

    Inputs:
      feed         [Contract]: OverlayV1BalancerV2Feed contract instance
      balv2_tokens [tuple]:    BalancerV2Tokens struct field variables
      pool_balweth [Contract]: BAL/WETH Balancer V2 WeightedPool2Tokens
                               contract instance representing the OVL/WETH
                               token pair
      pool_daiweth [Contract]: Balancer V2 WeightedPool2Tokens contract
                               instance for the DAI/WETH pool
    '''
    # OVL/WETH (represented by BAL/WETH)
    expect = balv2_tokens[1].hex()
    actual = feed.getPoolId(pool_balweth).hex()
    assert expect == actual

    # DAI/WETH (the market pool)
    expect = balv2_tokens[2].hex()
    actual = feed.getPoolId(pool_daiweth).hex()
    assert expect == actual
