# Security Review

For this security review we used [Auditor-Toolbox](https://github.com/Deivitto/auditor-docker).

## Check enviroment configuration.

1. The project was moved from Ethereum to Arbitrum. Thus the `brownie-config.yaml` has to be modified.

```diff
# use Ganache's forked mainnet mode as the default network
networks:
-  default: mainnet-fork
+  default: arbitrum-main-fork
```

And manually added Arbitrum Fork

```
whitehat@c9a45d1457b3:~/v1-core$ brownie networks add Development arbitrum-main-fork name="Ganache-CLI (Aribtrum-Mainnet Fork)" host=http://127.0.0.1 cmd=ganache-cli accounts=10 evm_version=istanbul fork=arbitrum-main mnemonic=brownie port=8545
Brownie v1.19.3 - Python development framework for Ethereum

SUCCESS: A new network 'Ganache-CLI (Aribtrum-Mainnet Fork)' has been added
  └─Ganache-CLI (Aribtrum-Mainnet Fork)
    ├─id: arbitrum-main-fork
    ├─cmd: ganache-cli
    ├─cmd_settings: {'accounts': 10, 'evm_version': 'istanbul', 'fork': 'arbitrum-main', 'mnemonic': 'brownie', 'port': 8545}
    └─host: http://127.0.0.1
```

Mod network config to use API key

```
whitehat@c9a45d1457b3:~/v1-core$ brownie networks modify arbitrum-main host="https://arbitrum-mainnet.infura.io/v3/\$WEB3_INFURA_PROJECT_ID" provider=infura
Brownie v1.19.3 - Python development framework for Ethereum

SUCCESS: Network 'Mainnet' has been modified
  └─Mainnet
    ├─id: arbitrum-main
    ├─chainid: 42161
    ├─explorer: https://api.arbiscan.io/api
    ├─host: https://arbitrum-mainnet.infura.io/v3/$WEB3_INFURA_PROJECT_ID
    ├─multicall2: 0x5B5CFE992AdAC0C9D48E05854B2d91C73a003858
    └─provider: infura
```

We have to change the .env config to replacing ETHERSCAN_TOKEN with ARIBSCAN_TOKEN
https://github.com/eth-brownie/brownie/blob/bc7b511583060fdaff1d4b5269aedcc1cb710bc6/brownie/network/contract.py#L84

## Run Brownie Tests

```
165 passed, 97 warnings, 146 errors in 389.36s (0:06:29)
```

After [928db2f](https://github.com/overlay-market/v1-core/commit/928db2feec5a2e3566800f6c0984b53df460d9a3)

```
201 passed, 1902 warnings, 110 errors in 957.30s (0:15:57)
```

After [ac43364](https://github.com/overlay-market/v1-core/commit/ac43364f5e17281da729405b8dc038b1a890d45e)

```
23 failed, 288 passed, 5876 warnings in 5464.02s (1:31:04)
```

Using `brownie test --failfast`

```
17 failed, 294 passed, 5227 warnings in 3495.36s (0:58:15)
```

After Reducing 10x Max Notinal Value [2390368](https://github.com/overlay-market/v1-core/commit/23903684738eff74d1063a472d6bab67efe31a04)

```
10 failed, 301 passed, 5788 warnings in 3759.36s (1:02:39)
```

## Failing Tests

### tests/factories/feed/univ3/test_deploy_feed.py::test_deploy_feed_creates_quanto_feed_without_reserve

```
>       tx = factory_without_reserve.deployFeed(market_base_token,
                                                market_quote_token,
                                                market_fee,
                                                market_base_amount,
                                                {'from': alice})
E       brownie.exceptions.VirtualMachineError: revert: OVLV1: marketCardinality < min
```

### tests/factories/feed/univ3/test_deploy_feed.py::test_deploy_no_reserve_feed_reverts_when_feed_already_exists

```
>       assert factory_without_reserve.isFeed(feed) is True
E       AssertionError: assert False is True
E        +  where False = <ContractCall 'isFeed(address)'>('0x0000000000000000000000000000000000000000')
E        +    where <ContractCall 'isFeed(address)'> = <OverlayV1NoReserveUniswapV3Factory Contract '0x26f15335BB1C6a4C0B660eDd694a0555A9F1cce3'>.isFeed
```

### tests/factories/feed/univ3/test_deploy_feed.py::test_deploy_feed_creates_quanto_feed

```
>       tx = factory.deployFeed(market_base_token, market_quote_token, market_fee,
                                market_base_amount, ovlweth_base_token,
                                ovlweth_quote_token, ovlweth_fee, {"from": alice})
E       brownie.exceptions.VirtualMachineError: revert: OVLV1: marketCardinality < min
```

### tests/factories/feed/univ3/test_deploy_feed.py::test_deploy_feed_reverts_when_feed_already_exists

```
>       assert factory.isFeed(feed) is True
E       AssertionError: assert False is True
E        +  where False = <ContractCall 'isFeed(address)'>('0x0000000000000000000000000000000000000000')
E        +    where <ContractCall 'isFeed(address)'> = <OverlayV1UniswapV3Factory Contract '0xFbD588c72B438faD4Cf7cD879c8F730Faa213Da0'>.isFeed
```

### tests/factories/market/test_conftest.py::test_market_fixture

```
>       assert expect_params == actual_params
E       assert [122000000000...00000000, ...] == [122000000000...00000000, ...]
E         At index 14 diff: 14 != 0
E         Use -v to get the full diff
```

### tests/feeds/uniswapv3/test_views.py::test_get_reserve_in_weth_for_daiweth

```
>       assert approx(expect_reserve) == actual_reserve
E       assert 193925431867444459208704 ± 1.9e+17 == 775651826277244056053208325
E        +  where 193925431867444459208704 ± 1.9e+17 = approx(193925431867444459208704)
```

### tests/feeds/uniswapv3/test_views.py::test_get_reserve_in_ovl

```
>       assert approx(expect_reserve_in_ovl) == actual_reserve_in_ovl
E       assert 853461373186892496896 ± 8.5e+14 == 3413625878742903797128978
E        +  where 853461373186892496896 ± 8.5e+14 = approx(853461373186892496896)
```

### tests/feeds/uniswapv3/test_views.py::test_get_reserve_in_weth_for_uniweth

```
>       assert approx(expect_reserve) == actual_reserve
E       assert 6772916291491569074176 ± 6.8e+15 == 1538957424546881555826202
E        +  where 6772916291491569074176 ± 6.8e+15 = approx(6772916291491569074176)
```

### tests/markets/test_build.py::test_build_reverts_when_oi_greater_than_cap

```
>       tx = market.build(input_collateral, input_leverage, input_is_long,
                          input_price_limit, {"from": alice})
E       brownie.exceptions.VirtualMachineError: revert: OVLV1:oi>cap
```

### tests/markets/test_build.py::test_build_reverts_when_liquidatable

```
        # check build reverts when position is liquidatable
        input_notional = Decimal(cap_notional) * volume * Decimal(1 + tol)
        input_collateral = int((input_notional / leverage))
        with reverts("OVLV1:liquidatable"):
>           _ = mock_market.build(input_collateral, input_leverage, input_is_long,
                                  input_price_limit, {"from": alice})
E           AssertionError: Transaction did not revert
```
