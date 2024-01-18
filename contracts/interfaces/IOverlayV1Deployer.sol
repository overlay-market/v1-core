// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

interface IOverlayV1Deployer {
    function deploy(address feed) external returns (address);

    function parameters()
        external
        view
        returns (
            address ov_,
            address feed_,
            address factory_
        );
}
