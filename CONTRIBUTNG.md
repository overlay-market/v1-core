# Contribution Guide

Overlay Protocol is an open source endeavor 

## Setting up your environment

Our project uses build systems Brownie (pre summer 2022) and Foundry. 

### Brownie setup entails:

- Python >= 3.9.2
- [Brownie >= 1.17.2](https://github.com/eth-brownie/brownie)
- Local Ganache environment installed
- `.env` file in project root with format

```
# required environment variables
export WEB3_INFURA_PROJECT_ID=<INFURA_TOKEN>
export WEB3_ALCHEMY_PROJECT_ID=<ALCHEMY_TOKEN>
export ETHERSCAN_TOKEN=<ETHERSCAN_TOKEN>
```

- `ETHERSCAN_TOKEN`: Creating an API key in [Etherscan's API docs](https://docs.etherscan.io/getting-started/viewing-api-usage-statistics)
- `WEB3_INFURA_PROJECT_ID`: Getting Started in [Infura's API docs](https://infura.io/docs)

[Instructions to install Brownie can be found here](https://eth-brownie.readthedocs.io/en/stable/install.html)

### Foundry setup entails:

[Instruction to install Foundry can be found here](https://book.getfoundry.sh/getting-started/installation)

## Workflow for contributions

New features must achieve full test coverage of their contributions. At the same time, they must not break any prior tests. 

Once a feature is complete, a pull request can be submitted for review, requiring the sign off of two core contributors.

Once successful signoff has occurred, congratulations. You are a successful contributor. 
