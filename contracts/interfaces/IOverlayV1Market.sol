// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

interface IOverlayV1Market {
    // immutables
    function ovl() external view returns (address);
    function feed() external view returns (address);
    function factory() external view returns (address);

    // risk params
    function k() external view returns (uint256);
    function lmbda() external view returns (uint256);
    function delta() external view returns (uint256);
    function capPayoff() external view returns (uint256);
    function capOi() external view returns (uint256);
    function capLeverage() external view returns (uint256);
    function circuitBreakerWindow() external view returns (uint256);
    function circuitBreakerMintTarget() external view returns (uint256);
    function maintenanceMargin() external view returns (uint256);
    function maintenanceMarginBurnRate() external view returns (uint256);
    function tradingFeeRate() external view returns (uint256);
    function minCollateral() external view returns (uint256);

    // trading fee related quantities
    function tradingFeeRecipient() external view returns (address);

    // funding related quantities
    function timestampFundingLast() external view returns (uint256);
}
