// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity 0.8.10;

interface IERC20 {
    function transfer(address to, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}


interface IDisperse {
    function disperseEther(
      address[] calldata recipients, 
      uint256[] calldata values
    ) external payable;

    function disperseToken(
      IERC20 token, 
      address[] calldata recipients, 
      uint256[] calldata values
    ) external;

    function disperseTokenSimple(
      IERC20 token, 
      address[] calldata recipients, 
      uint256[] calldata values
    ) external;
}
