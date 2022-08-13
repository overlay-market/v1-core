// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

interface IOverlayV1Portal {
  
  function dispatch(
    uint16 _chainId,
    address _portal,
    uint256 _amount
  ) external;

  function conjure (
    address _to,
    uint256 _amount
  ) external;

}
