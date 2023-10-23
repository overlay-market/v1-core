// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test} from "forge-std/Test.sol";

import {OverlayV1Token} from "../../contracts/OverlayV1Token.sol";
import {MINTER_ROLE, TRANSFER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";

contract OverlayV1TokenTest is Test {
    OverlayV1Token token;

    uint256 constant TOTAL_SUPPLY = 100_000e18;

    address ALICE = makeAddr("alice");
    address BOB = makeAddr("bob");
    address MARKET = makeAddr("market");

    function setUp() public {
        token = new OverlayV1Token();

        token.grantRole(TRANSFER_ROLE, MARKET);

        // Mint TOTAL_SUPPLY to the default admin (i.e. this contract)
        deal(address(token), address(this), TOTAL_SUPPLY, true);
    }

    function test_transfer_whitelisted() public {
        deal(address(token), ALICE, 100);
        
        vm.startPrank(ALICE);

        token.transfer(MARKET, 100); // transfer to whitelisted address

        assertEq(token.balanceOf(ALICE), 0);

        changePrank(MARKET);

        token.transfer(ALICE, 100); // transfer from whitelisted address

        assertEq(token.balanceOf(ALICE), 100);
    }

    function test_transfer_notWhitelisted() public {
        deal(address(token), ALICE, 100);
        
        vm.startPrank(ALICE);

        vm.expectRevert("ERC20: cannot transfer");
        token.transfer(BOB, 100);
    }

    function test_unlockTransfers_authorized() public {
        deal(address(token), ALICE, 100);

        vm.startPrank(ALICE);

        vm.expectRevert("ERC20: cannot transfer");
        token.transfer(BOB, 100);

        vm.stopPrank();

        token.unlockTransfers();

        vm.startPrank(ALICE);

        token.transfer(BOB, 100);

        assertEq(token.balanceOf(ALICE), 0);
    }

    function test_unlockTransfers_unauthorized() public {
        vm.startPrank(ALICE);

        vm.expectRevert("AccessControl: account 0x328809bc894f92807417d2dad6b7c998c1afdac6 is missing role 0x0000000000000000000000000000000000000000000000000000000000000000");
        token.unlockTransfers();
    }

    function test_addToWhitelist_authorized() public {
        token.grantRole(TRANSFER_ROLE, BOB);

        assertTrue(token.hasRole(TRANSFER_ROLE, BOB));
    }

    function test_addToWhitelist_unauthorized() public {
        vm.startPrank(ALICE);

        vm.expectRevert("AccessControl: account 0x328809bc894f92807417d2dad6b7c998c1afdac6 is missing role 0x0000000000000000000000000000000000000000000000000000000000000000");
        token.grantRole(TRANSFER_ROLE, BOB);
    }
}
