// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";

import "./interfaces/IOverlayV1Token.sol";

contract OverlayV1Token is IOverlayV1Token, AccessControlEnumerable, ERC20("Overlay", "OVL") {
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    modifier onlyMinter() {
        require(hasRole(MINTER_ROLE, msg.sender), "ERC20: !minter");
        _;
    }

    modifier onlyBurner() {
        require(hasRole(BURNER_ROLE, msg.sender), "ERC20: !burner");
        _;
    }

    function mint(address _recipient, uint256 _amount) external onlyMinter {
        _mint(_recipient, _amount);
    }

    function burn(uint256 _amount) external onlyBurner {
        _burn(msg.sender, _amount);
    }
}
