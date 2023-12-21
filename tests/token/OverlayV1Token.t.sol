// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test} from "forge-std/Test.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import "contracts/interfaces/IOverlayV1Token.sol";

contract OverlayV1TokenTest is Test {
    OverlayV1Token token;

    //-----------USERS-----------//
    address private immutable ADMIN = makeAddr("ADMIN");
    address private immutable MARKET_ONE = makeAddr("MARKET_ONE");
    address private immutable MARKET_TWO = makeAddr("MARKET_TWO");
    address private immutable MARKET_THREE = makeAddr("MARKET_THREE");
    address private immutable EMERGENCY = makeAddr("EMERGENCY");
    address private immutable USER = makeAddr("USER");

    function setUp() public {
        vm.startPrank(ADMIN);
        token = new OverlayV1Token();

        // grant EMERGENCY_ROLE to EMERGENCY
        token.grantRole(EMERGENCY_ROLE, EMERGENCY);

        // grant MINTER_ROLE to MARKET_ONE, MARKET_TWO, MARKET_THREE
        token.grantRole(MINTER_ROLE, MARKET_ONE);
        token.grantRole(MINTER_ROLE, MARKET_TWO);
        token.grantRole(MINTER_ROLE, MARKET_THREE);

        // grant BURNER_ROLE to MARKET_ONE, MARKET_TWO, MARKET_THREE
        token.grantRole(BURNER_ROLE, MARKET_ONE);
        token.grantRole(BURNER_ROLE, MARKET_TWO);
        token.grantRole(BURNER_ROLE, MARKET_THREE);

        vm.stopPrank();
    }

    function testMarketMint(uint256 amount) public {
        vm.startPrank(MARKET_ONE);
        token.mint(USER, amount);
        vm.stopPrank();
        assertEq(token.balanceOf(USER), amount);
    }

    function testMarketBurn(uint256 amount) public {
        vm.startPrank(MARKET_ONE);
        token.mint(MARKET_ONE, amount);
        token.burn(amount);
        assertEq(token.balanceOf(MARKET_ONE), 0);
    }

    function testUserBurn(uint256 amount) public {
        vm.startPrank(MARKET_ONE);
        token.mint(MARKET_ONE, amount);
        vm.startPrank(USER);
        vm.expectRevert();
        token.burn(amount);
        assertEq(token.balanceOf(USER), 0);
    }

    function testEmergencyRoleRemoval() public {
        vm.startPrank(EMERGENCY);
        token.emergencyRoleRemoval(MARKET_ONE);
        vm.stopPrank();
        assertEq(token.hasRole(MINTER_ROLE, MARKET_ONE), false);
        assertEq(token.hasRole(BURNER_ROLE, MARKET_ONE), false);

        vm.startPrank(MARKET_ONE);
        vm.expectRevert();
        token.mint(MARKET_ONE, 100e18);

        vm.startPrank(MARKET_TWO);
        token.mint(USER, 100e18);

        assertEq(token.balanceOf(USER), 100e18);
    }
}
