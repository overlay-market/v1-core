// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";

contract TokenTest is Test {
    OverlayV1Token ov;
    address immutable MINTER = makeAddr("minter");
    address immutable BURNER = makeAddr("burner");
    address immutable USER = makeAddr("user");
    bytes32 constant MINTER_ROLE = keccak256("MINTER");
    bytes32 constant BURNER_ROLE = keccak256("BURNER");

    function setUp() public {
        ov = new OverlayV1Token();

        ov.grantRole(MINTER_ROLE, MINTER);
        ov.grantRole(BURNER_ROLE, BURNER);
    }

    function testMinter() public {
        vm.startPrank(MINTER);
        ov.mint(USER, 100);
        assertEq(ov.balanceOf(USER), 100);
    }

    function testBurner() public {
        vm.startPrank(MINTER);
        ov.mint(BURNER, 100);
        assertEq(ov.balanceOf(BURNER), 100);

        vm.startPrank(BURNER);
        ov.burn(100);
        assertEq(ov.balanceOf(BURNER), 0);
    }

    function testUser() public {
        vm.startPrank(MINTER);
        ov.mint(USER, 100);
        assertEq(ov.balanceOf(USER), 100);

        vm.startPrank(USER);
        vm.expectRevert(
            "AccessControl: account 0x6ca6d1e2d5347bfab1d91e883f1915560e09129d is missing role 0xf0887ba65ee2024ea881d91b74c2450ef19e1557f03bed3ea9f16b037cbe2dc9"
        );
        ov.mint(USER, 100);
        assertEq(ov.balanceOf(USER), 100);

        vm.expectRevert(
            "AccessControl: account 0x6ca6d1e2d5347bfab1d91e883f1915560e09129d is missing role 0x9667e80708b6eeeb0053fa0cca44e028ff548e2a9f029edfeac87c118b08b7c8"
        );
        ov.burn(100);
        assertEq(ov.balanceOf(USER), 100);
    }
}
