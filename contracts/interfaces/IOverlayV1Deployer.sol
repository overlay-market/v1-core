// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

interface IOverlayV1Deployer {
    function factory() external view returns (address);

    function ovl() external view returns (address);

    function deploy(address feed) external returns (address);

    function parameters()
        external
        view
        returns (
            address ovl_,
            address feed_,
            address factory_
        );
}
