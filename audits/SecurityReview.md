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
10 failed, 301 passed, 5788 warnings in 3759.36s (1:02:39
```
## Medusa Test

### Use solidity Version 0.8.10

`solc-select install 0.8.10`

`solc-select use 0.8.10`
