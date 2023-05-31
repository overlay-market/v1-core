// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../IOverlayV1Feed.sol";

interface IOverlayV1NFTPerpFeed is IOverlayV1Feed {
    function aggregator() external view returns (address);

    function description() external view returns (address);

    function decimals() external view returns (address);
}
