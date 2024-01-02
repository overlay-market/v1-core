# Review of differencies between Ethereum and Arbitrum

## Summary

This document is a review of the differences between Ethereum and Arbitrum. It is intended to verify if the differences between the two chains can cause any issue since OverlayV1 was designed to work on Ethereum.

Source: https://docs.arbitrum.io/for-devs/concepts/differences-between-arbitrum-ethereum/overview

### Block timestamps: Arbitrum vs. Ethereum

Along the repository `block.number` is not used, so we are going to focus on `block.timestamp`.

    As a general rule, any timing assumptions a contract makes about block numbers and timestamps should be considered generally reliable in the longer term (i.e., on the order of at least several hours) but unreliable in the shorter term (minutes). (It so happens these are generally the same assumptions one should operate under when using block numbers directly on Ethereum!)

Contracts that uses `block.timestamp`:
- OverlayV1Market.sol
- OverlayV1NoReserveUniswapV3Feed.sol
- OverlayV1UniswapV3Feed.sol (Get info from the Oracle using `block.timestamp`)
- OverlayV1FeedMock.sol

__Check `_payFunding()` function.__

Found two random consecutive blocks with the same timestamp. 
https://arbiscan.io/block/165062126
https://arbiscan.io/block/165062125

```solidity
    function _payFunding() private {
        // apply funding if at least one block has passed
        uint256 timeElapsed = block.timestamp - timestampUpdateLast;
        if (timeElapsed > 0) {
```

This function uses `block.timestamp` to calculate the time elapsed since the last update. If two consecutive blocks have the same timestamp, the time elapsed will be 0 and the function will not apply the funding.

Source: https://docs.arbitrum.io/for-devs/concepts/differences-between-arbitrum-ethereum/block-numbers-and-time#block-timestamps-arbitrum-vs-ethereum

### Solidity Version

We are currently compiling the code with version 0.8.10 so this should not be a problem.

    OPCODE PUSH0
    This OPCODE is not yet supported, but will soon be available. This means that solidity version 0.8.20 or higher can only be used with an evm-version lower than the default shanghai (see instructions here to change that parameter in solc, or here to set the solidity or evmVersion configuration parameters in hardhat). Versions up to 0.8.19 (included) are fully compatible.

### Check whether the Arbitrum Sequencer is active

[M-3: _validateAndGetPrice() doesn't check If Arbitrum sequencer is down in Chainlink feeds](https://solodit.xyz/issues/m-3-_validateandgetprice-doesnt-check-if-arbitrum-sequencer-is-down-in-chainlink-feeds-sherlock-bond-protocol-update-git)

[M-25: Missing checks for whether Arbitrum Sequencer is active](https://solodit.xyz/issues/m-25-missing-checks-for-whether-arbitrum-sequencer-is-active-sherlock-none-gmx-git)

Found this issue on Solodit that relates Chainlink feeds and Arbitrum sequencer. It is not related to the current audit, but it is a good point to take into account.

[Example code to check that the sequencer is up](https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code)

### Brownie config file

Review of the brownie config file to check if there is any relevant info about the network used to deploy the protocol.

```
# use Ganache's forked mainnet mode as the default network
networks:
  default: mainnet-fork
```
The project default network is `mainnet-fork`, which is a fork of the Ethereum mainnet.


Brownie [docs](https://eth-brownie.readthedocs.io/en/stable/config.html#networks) specify that to use Arbitrum you need to run the commands with the `--network arbitrum-main` flag.

Or we could simply modify the brownie config file to use Arbitrum as the default network.