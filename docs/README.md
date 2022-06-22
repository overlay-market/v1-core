# v1-core/docs

## Table of v1-core functions

Below is a table of `v1-core` functions and the associated sections and equations in the `v1-core` whitepaper (WP), based on [this draft](https://planckcat.mypinata.cloud/ipfs/QmVMX7DH8Kh22kxMyDFGUJcw1a3irNPvyZBtAogkyJYJEv).

| Function | Code Location | WP Location | Description |
| --- | --- | --- | --- |
| `build()` | `OverlayV1Market.sol#L140` |  | Builds a new position |
| `unwind()` | `OverlayV1Market.sol#L241` |  | Unwinds fraction of an existing position |
| `liquidate()` | `OverlayV1Market.sol#L376` |  | Liquidates a liquidatable position |
| `update()` | `OverlayV1Market.sol#L482` |  | Updates market: pays funding and fetches freshest data from feed |
| `dataIsValid()` | `OverlayV1Market.sol#L516` | Eqns. (58), (59), (60) | Sanity check on data fetched from oracle in case of manipulation |
| `oiAfterFunding()` | `OverlayV1Market.sol#L539`  | Eqns. (26), (27), (28); Ref Eqns. (14), (24) | Current open interest after funding payments transferred |
| `capOiAdjustedForCircuitBreaker()` | `OverlayV1Market.sol#L592` | Eqns. (75), (76); Ref Eqn. (72) | Current notional cap with adjustments lower in the event market has printed a lot in recent past |
| `circuitBreaker()` | `OverlayV1Market.sol#L608` | Eqn. (75); Ref Eqn. (72) | Bound on notional cap from circuit breaker  |
| `capNotionalAdjustedForBounds()` | `OverlayV1Market.sol#L628` | Eqns. (55), (56), (57) | Current notional cap with adjustments to prevent front-running trade and back-running trade |
| `frontRunBound()` | `OverlayV1Market.sol#L645` | Eqn. (55) | Bound on notional cap to mitigate front-running attack |
| `backRunBound()` | `OverlayV1Market.sol#L652` | Eqns. (56), (57) | Bound on notional cap to mitigate back-running attack |
| `oiFromNotional()` | `OverlayV1Market.sol#L661` | Eqn. (7); Ref Eqns. (6), (41) | Returns the open interest in number of contracts for a given notional |
| `bid()` | `OverlayV1Market.sol#L666` | Eqn. (38) | Bid price given oracle data and recent volume |
| `ask()` | `OverlayV1Market.sol#L679` | Eqn. (39) | Ask price given oracle data and recent volume |
| `_midFromFeed()` | `OverlayV1Market.sol#L693` | Eqn. (41) | Mid price without impact or spread given oracle data |
| `_registerVolumeBid()` | `OverlayV1Market.sol#L699` | Eqns. (42)-(46) | Rolling volume adjustments on bid side to be used for market impact |
| `_registerVolumeAsk()` | `OverlayV1Market.sol#L721` | Eqns. (42)-(46) | Rolling volume adjustments on ask side to be used for market impact |
| `_registerMintOrBurn()` | `OverlayV1Market.sol#L743` | Eqns. (74), (43)-(46) | Rolling mint or burn accumulator to be used for circuit breaker |
| `snapshot.transform()` | `libraries/Roller.sol#L28` | Eqns. (43)-(46) | Adjusts the accumulator value downward linearly over time based off amount of time passed in current window |
| `position.value()` | `libraries/Position.sol#L224` | Eqn. (9); Ref. Eqn. (4), (6), (7), (8), (10) | Computes the value of a position |
| `position.cost()` | `libraries/Position.sol#L211` | Eqn. (10); `tau = 0` | Computes the position's cost cast to uint256 |
| `position.liquidatable()` | `libraries/Position.sol#L316` | Eqn. (77); Ref Eqn. (9) | Whether a position can be liquidated |
