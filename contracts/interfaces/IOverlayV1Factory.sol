// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../libraries/Risk.sol";

import "./IOverlayV1Deployer.sol";
import "./IOverlayV1Token.sol";

interface IOverlayV1Factory {
    // risk param bounds
    function PARAMS_MIN(uint256 idx) external view returns (uint256);

    function PARAMS_MAX(uint256 idx) external view returns (uint256);

    // immutables
    function ovl() external view returns (IOverlayV1Token);

    function deployer() external view returns (IOverlayV1Deployer);

    // global parameter
    function feeRecipient() external view returns (address);

    // registry of supported feed factories
    function isFeedFactory(address feedFactory) external view returns (bool);

    // registry of markets; for a given feed address, returns associated market
    function getMarket(address feed) external view returns (address market_);

    // registry of deployed markets by factory
    function isMarket(address market) external view returns (bool);

    // adding feed factory to allowed feed types
    function addFeedFactory(address feedFactory) external;

    // removing feed factory from allowed feed types
    function removeFeedFactory(address feedFactory) external;

    // deploy new market
    function deployMarket(
        address feedFactory,
        address feed,
        uint256[15] calldata params
    ) external returns (address market_);

    // per-market risk parameter setters
    function setRiskParam(
        address feed,
        Risk.Parameters name,
        uint256 value
    ) external;

    // fee repository setter
    function setFeeRecipient(address _feeRecipient) external;
}
