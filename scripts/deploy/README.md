# Market/Feed Deployment Instructions

1. Make changes to `scripts/all_parameters.json`, ie, add the parameters and addresses corresponding to the contract you want to deploy
2. Run `deploy.py` like this: `brownie run scripts/deploy/deploy.py main ethereum_goerli --network goerli-fork`. This will post a tx the gnosis safe for deploying the contracts on L1 Goerli; prior to posting to safe, it will test whether the deployments are successful on a fork of L1 Goerli; and will do this only for undeployed contracts in `all_parameters.json`, ie, when a `feed_address` or `market_address` or `feed_factory_address` doesn't exist.
