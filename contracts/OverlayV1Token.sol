// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";

import "./interfaces/IOverlayV1Token.sol";

contract OverlayV1Token is IOverlayV1Token, AccessControlEnumerable, ERC20("Overlay", "OVL") {
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    modifier onlyMinter() {
        if (!hasRole(MINTER_ROLE, msg.sender)) revert NotMinter();
        _;
    }

    modifier onlyBurner() {
        if (!hasRole(BURNER_ROLE, msg.sender)) revert NotBurner();
        _;
    }

    modifier onlyEmergency() {
        if (!hasRole(EMERGENCY_ROLE, msg.sender)) revert NotEmergency();
        _;
    }

    function mint(address _recipient, uint256 _amount) external onlyMinter {
        _mint(_recipient, _amount);
    }

    function burn(uint256 _amount) external onlyBurner {
        _burn(msg.sender, _amount);
    }

    function emergencyRoleRemoval(address _account) external onlyEmergency {
        _revokeRole(BURNER_ROLE, _account);
        _revokeRole(MINTER_ROLE, _account);
    }
}
