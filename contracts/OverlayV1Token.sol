// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "openzeppelin/token/ERC20/ERC20.sol";
import "openzeppelin/access/AccessControlEnumerable.sol";

import "./interfaces/IOverlayV1Token.sol";

contract OverlayV1Token is IOverlayV1Token, AccessControlEnumerable, ERC20("Overlay", "OVL") {
    /// @notice indicates whether transfers are allowed for everyone or only whitelisted addresses
    bool public transfersLocked;

    constructor() {
        // Only whitelisted addresses can transfer by default
        transfersLocked = true;
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

    function unlockTransfers() external onlyRole(DEFAULT_ADMIN_ROLE) {
        transfersLocked = false;
    }

    function _beforeTokenTransfer(address from, address to, uint256)
        internal
        view
        override
    {
        require(
            !transfersLocked || hasRole(TRANSFER_ROLE, from) || hasRole(TRANSFER_ROLE, to),
            "ERC20: cannot transfer"
        );
    }
}
