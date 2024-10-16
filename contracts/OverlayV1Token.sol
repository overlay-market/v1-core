// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

import "./interfaces/IOverlayV1Token.sol";

contract OverlayV1Token is IOverlayV1Token, AccessControl, ERC20("Overlay Testnet", "OVL") {
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function mint(address _recipient, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_recipient, _amount);
    }

    function burn(uint256 _amount) external onlyRole(BURNER_ROLE) {
        _burn(msg.sender, _amount);
    }
}
