pragma solidity ^0.8.10;

import "@openzeppelin/contracts/token/erc20/erc20.sol";

contract TokenMock is ERC20 {

  constructor (
    string memory name, 
    string memory symbol, 
    uint256 amount
  ) ERC20(name, symbol) {

    _mint(msg.sender, amount);

  }

}
