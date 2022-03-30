// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

interface IOverlayV1Deployer {
    function factory() external view returns (address);

    function deploy(
        address ovl,
        address feed,
        uint256[15] calldata params
    ) external returns (address);
}
