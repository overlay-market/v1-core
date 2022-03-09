# v1-core/docs

## Table of v1-core functions

Below is a table of `v1-core` functions and the associated sections and equations in the `v1-core` whitepaper (WP), based on [this draft](https://planckcat.mypinata.cloud/ipfs/QmVYywKyNuZNDZdWFRzD8ehEd3oVkKsDTEJuoRL85DSDrj).

| Function | Code Location | WP Location | Description |
| --- | --- | --- | --- |
| `build()` | `OverlayV1Market.sol#L145` |  | Builds a new position |
| `unwind()` | `OverlayV1Market.sol#L240` |  | Unwinds fraction of an existing position |
| `liquidate()` | `OverlayV1Market.sol#L345` |  | Liquidates a liquidatable position |
| `update()` | `OverlayV1Market.sol#L431` |  | Updates market: pays funding and fetches freshest data from feed |
| `dataIsValid()` | `OverlayV1Market.sol#L465` | Eqns. (56), (57), (58) | Sanity check on data fetched from oracle in case of manipulation |
| `oiAfterFunding()` | `OverlayV1Market.sol#L488`  | Eqns. (25), (26), (27); Ref Eqns. (13), (23) | Current open interest after funding payments transferred |
| `capNotionalAdjustedForCircuitBreaker()` | `OverlayV1Market.sol#L543` | Eqns. (73), (74); Ref Eqn. (69) | Current notional cap with adjustments lower in the event market has printed a lot in recent past |
| `circuitBreaker()` | `OverlayV1Market.sol#L558` | Eqn. (73); Ref Eqn. (69) | Bound on notional cap from circuit breaker  |
| `capNotionalAdjustedForBounds()` | `OverlayV1Market.sol#L578` | Eqns. (54), (55) | Current notional cap with adjustments to prevent front-running trade and back-running trade |
| `frontRunBound()` | `OverlayV1Market.sol#L595` | Eqn. (54) | Bound on notional cap to mitigate front-running attack |
| `backRunBound()` | `OverlayV1Market.sol#L601` | Eqn. (55); `wo / (wo + wi) = 1/2` | Bound on notional cap to mitigate back-running attack |
| `oiFromNotional()` | `OverlayV1Market.sol#L611` | Eqn. (7); Ref Eqns. (6), (40) | Returns the open interest in number of contracts for a given notional |
| `bid()` | `OverlayV1Market.sol#L621` | Eqn. (37) | Bid price given oracle data and recent volume |
| `ask()` | `OverlayV1Market.sol#L632` | Eqn. (38) | Ask price given oracle data and recent volume |
| `_midFromFeed()` | `OverlayV1Market.sol#L653` | Eqn. (40) | Mid price without impact/spread given oracle data and recent volume |
| `_registerVolumeBid()` | `OverlayV1Market.sol#L661` | Eqns. (41), (42), (43), (44), (45) | Rolling volume adjustments on bid side to be used for market impact |
| `_registerVolumeAsk()` | `OverlayV1Market.sol#L683` | Eqns. (41), (42), (43), (44), (45) | Rolling volume adjustments on ask side to be used for market impact |
| `_registerMint()` | `OverlayV1Market.sol#L704` | Eqns. (74), (42), (43), (44), (45) | Rolling mint accumulator to be used for circuit breaker |
| `snapshot.transform()` | `libraries/Roller.sol#L23` | Eqns. (42), (43), (44), (45) | Adjusts the accumulator value downward linearly over time based off amount of time passed in current window |
| `position.value()` | `libraries/Position.sol#L133` | Eqn. (8); Ref. Eqn. (4), (6), (7), (9) | Computes the value of a position |
| `position.cost()` | `libraries/Position.sol#L120` | Eqn. (9); `tau = 0` | Computes the position's cost cast to uint256 |
| `position.liquidatable()` | `libraries/Position.sol#L221` | Eqn. (75); Ref Eqn. (8) | Whether a position can be liquidated |
