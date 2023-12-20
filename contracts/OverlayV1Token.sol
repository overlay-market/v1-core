// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";

import "./interfaces/IOverlayV1Token.sol";

contract OverlayV1Token is IOverlayV1Token, AccessControlEnumerable, ERC20("Overlay", "OV") {
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function mint(address _recipient, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_recipient, _amount);
    }

    function burn(uint256 _amount) external onlyRole(BURNER_ROLE) {
        _burn(msg.sender, _amount);
    }

    function emergencyRoleRemoval(address _account) external onlyRole(EMERGENCY_ROLE) {
        _revokeRole(BURNER_ROLE, _account);
        _revokeRole(MINTER_ROLE, _account);
    }
}
