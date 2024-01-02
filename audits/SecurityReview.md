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

## Run Brownie Tests

```
165 passed, 97 warnings, 146 errors in 389.36s (0:06:29)
```

## Medusa Test

### Use solidity Version 0.8.10

`solc-select install 0.8.10`
`solc-select use 0.8.10`