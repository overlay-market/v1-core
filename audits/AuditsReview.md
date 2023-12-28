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

### 5.2.1 Rounding down of `snapAccumulator` might influence calculations

>Overlay: Confirmed and agreed. Fixed in commit [9b1865e](https://github.com/overlay-market/v1-core/tree/9b1865e).

Github Message: This commit does not belong to any branch on this repository, and may belong to a fork outside of the repository.

*Warning*: In commit [9b1865e](https://github.com/overlay-market/v1-core/tree/9b1865e) `Roller.sol` is "fixed" but when is compared against Main the modification is reverted 😨. [Check Diff](https://github.com/overlay-market/v1-core/compare/9b1865e..ad3d152).

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

Overlay: Fixed in [7fe8ff3](https://github.com/overlay-market/v1-core/pull/44/commits/7fe8ff3a2155e67e15a0a6e88415bb400f140c68).

Note: the segment of code fixed in the mentioned commit remains untouched in Main branch 😊. [Check Diff](https://github.com/overlay-market/v1-core/compare/1ce980a..main)


### 5.3.4 Verify the validity of `_microWindow` and `_macroWindow`

>Overlay: Fixed in commit [44b419c](https://github.com/overlay-market/v1-core/pull/44/commits/44b419c254ebb532b844434ecdb248bacbf7bc73). Except for the 3rd recommendation.

Note: the segment of code fixed in the mentioned commit is removed in Main branch 😨. [Check Diff](https://github.com/overlay-market/v1-core/compare/44b419c..main)

### 5.3.5 Simplify `_midFromFeed()`

>Overlay: Fixed in commit [2bb5654](https://github.com/overlay-market/v1-core/pull/39/commits/2bb565498a771613ab3eeb49e79b035e4a80e79e).

Note: the segment of code fixed in the mentioned commit remains untouched in Main branch 😊. [Check Diff](https://github.com/overlay-market/v1-core/compare/2bb5654..main)

-------------------------------------------------------------------------------
### Compare deployed beta against audited version
https://github.com/overlay-market/v1-core/compare/24dffd5..ad3d152

## Missing code4rena report in landing page

https://code4rena.com/reports/2021-11-overlay