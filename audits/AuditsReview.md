# Shutdown Analysis

__Shutdown__ functionality was added after the audit. The following analysis is based on the current version of the code.

[Line 66](https://github.com/overlay-market/v1-core/blob/main/contracts/OverlayV1Market.sol#L66) of `OverlayV1Market.sol`: Variable `isShutdown` could be private since it is only used internally in the contract.

[Line 933](https://github.com/overlay-market/v1-core/blob/main/contracts/OverlayV1Market.sol#L933) of `OverlayV1Market.sol`: Function `shutdown()` does not need `notShutdown`modifier since it only set the variable `isShutdown` to true.

[Line 946](https://github.com/overlay-market/v1-core/blob/main/contracts/OverlayV1Market.sol#L946) of `OverlayV1Market.sol`: Not necessary to cache `fraction` since it is only used once.

# [Least Authority Audit Review](https://github.com/overlay-market/v1-core/tree/main/audits/leastauthority)

>Specifically, we examined the Git revision for our initial review:
>[c480f6f9af526d4c15f16a3442b2d090197cfb76](https://github.com/overlay-market/v1-core/commit/c480f6f9af526d4c15f16a3442b2d090197cfb76)

>For the verification, we examined the Git revision:
>[24dffd529068cf3d3e8b3599a06d9aebfd212e37](https://github.com/overlay-market/v1-core/commit/24dffd529068cf3d3e8b3599a06d9aebfd212e37)

## Specific Issues & Suggestions Review

### Suggestion 1: Improve Error Handling

Note: this suggestion was ignored.

### Suggestion 2: Remove Unused Code

Note: solved in [24dffd5](https://github.com/overlay-market/v1-core/commit/24dffd529068cf3d3e8b3599a06d9aebfd212e37) and remains unchanged 😊

### Suggestion 3: Remove Redundant Lines in OverlayV1Token Constructor

Note: solved in [24dffd5](https://github.com/overlay-market/v1-core/commit/24dffd529068cf3d3e8b3599a06d9aebfd212e37) and remains unchanged 😊

### Suggestion 4: Simplify toInt192Bounded

Note: solved in [24dffd5](https://github.com/overlay-market/v1-core/commit/24dffd529068cf3d3e8b3599a06d9aebfd212e37) and remains unchanged 😊

### Suggestion 5: Replace _setupRole with _grantRole

Note: solved in [24dffd5](https://github.com/overlay-market/v1-core/commit/24dffd529068cf3d3e8b3599a06d9aebfd212e37) and remains unchanged 😊

### Suggestion 6: Use Multiple Oracles for Feeds

Note: this suggestion was ignored.

### Suggestion 7: Create A Long-Duration Simulation to Test Properties

Note: this suggestion was ignored. We could use Foundry or Echidna, to do it. Tool that at the moment of the audit were not available.

### Suggestion 8: Make Positions Transferable

Note: this suggestion was ignored.

### Suggestion 9: Improve Documentation

Note: this suggestion was ignored.

# [Spearbit Audit Review](https://github.com/overlay-market/v1-core/blob/main/audits/spearbit/audit.pdf)

## Findings Review

### 5.1.1 Use `unchecked` in `TickMath.sol` and `FullMath.sol`

>*Recommendation*: Add an unchecked block to the following functions in TickMath.sol and FullMath.sol:
>
>• getSqrtRatioAtTick()
>
>• getTickAtSqrtRatio()
>
>• mulDiv()
>
>• mulDivRoundingUp()

Check: 
- getSqrtRatioAtTick() -> OK
- getTickAtSqrtRatio() -> NOT USED
- mulDiv() -> OK
- mulDivRoundingUp() -> NOT USED

Note: We have custom versions of TickMath.sol and FullMath.sol but we have copy pasted functions that we are not using 🤔.

### 5.1.2 Liquidation might fail

>Fixed in commit [082c6c7](https://github.com/overlay-market/v1-core/tree/082c6c71ea3f65a0ce20cae4a9ca895656a0690e).

Github Message: This commit does not belong to any branch on this repository, and may belong to a fork outside of the repository.

*Warning*: function `liquidate()` has been changed after the audit 😔. [Check Diff](https://github.com/overlay-market/v1-core/compare/082c6c7..ad3d152).

Review:

- Added `notShutdown` modifier: https://github.com/overlay-market/v1-core/blob/main/contracts/OverlayV1Market.sol#L387

- This check is duplicated in `liquidate()` and `unwind()` could be extracted to an internal function.

    ```solidity
    if (pos.isLong) {
        oiLong = oiLong.subFloor(
            pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide)
        );
        oiLongShares -= pos.oiSharesCurrent(fraction);
    } else {
        oiShort = oiShort.subFloor(
            pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide)
        );
        oiShortShares -= pos.oiSharesCurrent(fraction);
    }
    ```

- Spearbit "5.4.2 Set pos.entryPrice to 0 after liquidation" recommendation is reverted.
    
    >Recommendation: Consider setting pos.entryPrice to 0. This is more in line with the rest of the code and can give a small gas refund.

    In the updated version, `notionalInitial` and `debtInitial` could be set to 0, unless there is a reason to keep those values.

### 5.2.1 Rounding down of `snapAccumulator` might influence calculations

>Overlay: Confirmed and agreed. Fixed in commit [9b1865e](https://github.com/overlay-market/v1-core/tree/9b1865e).

Github Message: This commit does not belong to any branch on this repository, and may belong to a fork outside of the repository.

*Warning*: In commit [9b1865e](https://github.com/overlay-market/v1-core/tree/9b1865e) `Roller.sol` is "fixed" but when is compared against Main the modification is reverted 😨. [Check Diff](https://github.com/overlay-market/v1-core/compare/9b1865e..ad3d152).

Update: This was removed in https://github.com/overlay-market/v1-core/commit/24dffd529068cf3d3e8b3599a06d9aebfd212e37

### 5.2.2 Verify pool legitimacy

>Overlay: Fixed in commit [b889200](https://github.com/overlay-market/v1-core/pull/45/commits/b889200e87fc7c77ed8003a779ce4fb2068f8761).

Note: the segment of code fixed in the mentioned commit is modified in Main branch 😔. [Check Diff](https://github.com/overlay-market/v1-core/compare/b889200..ad3d152)

### 5.3.1 Liquidatable positions can be unwound by the owner of the position

>Overlay: Disallowed unwinding of liquidatable position in commit [0d6f1c4](https://github.com/overlay-market/v1-core/pull/44/commits/0d6f1c4e689cc59bcbc0deb055e87397af60d24e).

Note: the segment of code fixed in the mentioned commit is modified in Main branch 😔. [Check Diff](https://github.com/overlay-market/v1-core/compare/0d6f1c4..ad3d152)

### 5.3.2 Adding constructor params causes creation code to change

>Overlay: Fixed in commit [1ce980a](https://github.com/overlay-market/v1-core/pull/44/commits/1ce980a956b1eada94786979e1083d6e7f35b903).

Note: the segment of code fixed in the mentioned commit is modified in Main branch 😔. [Check Diff](https://github.com/overlay-market/v1-core/compare/1ce980a..main)

### 5.3.3 Potential wrap of timestamp

>Overlay: Fixed in [7fe8ff3](https://github.com/overlay-market/v1-core/pull/44/commits/7fe8ff3a2155e67e15a0a6e88415bb400f140c68).

Note: the segment of code fixed in the mentioned commit remains untouched in Main branch 😊. [Check Diff](https://github.com/overlay-market/v1-core/compare/1ce980a..main)


### 5.3.4 Verify the validity of `_microWindow` and `_macroWindow`

>Overlay: Fixed in commit [44b419c](https://github.com/overlay-market/v1-core/pull/44/commits/44b419c254ebb532b844434ecdb248bacbf7bc73). Except for the 3rd recommendation.

Note: the segment of code fixed in the mentioned commit is removed in Main branch 😨. [Check Diff](https://github.com/overlay-market/v1-core/compare/44b419c..main)

Update: Removed from `contracts/feeds/OverlayV1Feed.sol` at https://github.com/overlay-market/v1-core/pull/45 but added in `contracts/feeds/OverlayV1Feed.sol`

### 5.3.5 Simplify `_midFromFeed()`

>Overlay: Fixed in commit [2bb5654](https://github.com/overlay-market/v1-core/pull/39/commits/2bb565498a771613ab3eeb49e79b035e4a80e79e).

Note: the segment of code fixed in the mentioned commit remains untouched in Main branch 😊. [Check Diff](https://github.com/overlay-market/v1-core/compare/2bb5654..main)

-------------------------------------------------------------------------------
### Compare deployed beta against audited version
https://github.com/overlay-market/v1-core/compare/24dffd5..ad3d152

## Missing code4rena report in landing page

https://code4rena.com/reports/2021-11-overlay