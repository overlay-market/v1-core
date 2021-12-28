# v1-core

V1 core smart contracts


## Diagram

![diagram](./docs/assets/diagram.svg)


## Modules

V1 core relies on three modules:

- [Feeds Module](./contracts/feeds)
- [Markets Module](./contracts/OverlayV1Market.sol)
- [OVL Module](./contracts/OverlayV1Token.sol)


### Feeds Module

When adding support for a new type of oracle feed, developers should inherit from [`OverlayV1Feed.sol`](./contracts/feeds/OverlayV1Feed.sol) and implement the internal function `_fetch()` for the required integration with the oracle provider.

`_fetch()` retrieves data from the oracle provider and organizes the data in a general format, `Oracle.Data`, as specified in the [`Oracle.sol`](./contracts/libraries/Oracle.sol) library.

`Oracle.Data` data is consumed by each deployment of `OverlayV1Market.sol` for traders to take positions on the market of interest.
