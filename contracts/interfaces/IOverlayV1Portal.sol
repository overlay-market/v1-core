// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

interface IOverlayV1Portal {

  event Dispatched(address from, uint256 amount);
  event Conjured(address to, uint256 amount);
  
  function dispatch(
    uint16 _chainId,
    address _portal,
    uint256 _amount
  ) external payable;

}
