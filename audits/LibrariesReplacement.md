# List of custom libraries that could be replaced by standard ones

`libraries/Cast.sol` with https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/math/SafeCast.sol

`libraries/FixedPoint.sol` with https://github.com/Vectorized/solady/blob/main/src/utils/FixedPointMathLib.sol

`libraries/LogExpMath.sol` is only being used in FixedPoint.sol, so it also can be replaced.

`libraries/uniswap/*` with https://github.com/Uniswap/v3-core/blob/0.8/ __this branch is not protected__
