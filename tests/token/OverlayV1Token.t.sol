// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test} from "forge-std/Test.sol";

import {OverlayV1Token} from "../../contracts/OverlayV1Token.sol";
import {MINTER_ROLE, BURNER_ROLE, TRANSFER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";

contract OverlayV1TokenTest is Test {
    OverlayV1Token token;

    uint256 constant TOTAL_SUPPLY = 100_000e18;

    address ALICE = makeAddr("alice");
    address BOB = makeAddr("bob");
    address MARKET = makeAddr("market");

    function setUp() public {
        token = new OverlayV1Token();

        token.grantRole(MINTER_ROLE, address(this));
        token.grantRole(BURNER_ROLE, address(this));
        token.grantRole(TRANSFER_ROLE, address(this));
        token.grantRole(TRANSFER_ROLE, MARKET);
    }

    // --------- OVL changes specific tests ---------

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

    // --------- Base ERC20 tests ---------
    // Reference: https://github.com/transmissions11/solmate/blob/main/src/test/ERC20.t.sol

    function invariantMetadata() public {
        assertEq(token.name(), "Overlay");
        assertEq(token.symbol(), "OVL");
        assertEq(token.decimals(), 18);
    }

     function testMint() public {
        token.mint(MARKET, 1e18);

        assertEq(token.totalSupply(), 1e18);
        assertEq(token.balanceOf(MARKET), 1e18);
    }

    function testBurn() public {
        token.mint(address(this), 1e18);
        token.burn(0.9e18);

        assertEq(token.totalSupply(), 1e18 - 0.9e18);
        assertEq(token.balanceOf(address(this)), 0.1e18);
    }

    function testApprove() public {
        assertTrue(token.approve(address(0xBEEF), 1e18));

        assertEq(token.allowance(address(this), address(0xBEEF)), 1e18);
    }

    function testTransfer() public {
        token.mint(address(this), 1e18);

        assertTrue(token.transfer(MARKET, 1e18));
        assertEq(token.totalSupply(), 1e18);

        assertEq(token.balanceOf(address(this)), 0);
        assertEq(token.balanceOf(MARKET), 1e18);
    }

    function testTransferFrom() public {
        address from = MARKET;

        token.mint(from, 1e18);

        vm.prank(from);
        token.approve(address(this), 1e18);

        assertTrue(token.transferFrom(from, address(0xBEEF), 1e18));
        assertEq(token.totalSupply(), 1e18);

        assertEq(token.allowance(from, address(this)), 0);

        assertEq(token.balanceOf(from), 0);
        assertEq(token.balanceOf(address(0xBEEF)), 1e18);
    }

    function testFailTransferInsufficientBalance() public {
        token.mint(address(this), 0.9e18);
        token.transfer(address(0xBEEF), 1e18);
    }

    function testFailTransferFromInsufficientAllowance() public {
        address from = MARKET;

        token.mint(from, 1e18);

        vm.prank(from);
        token.approve(address(this), 0.9e18);

        token.transferFrom(from, address(0xBEEF), 1e18);
    }

    function testFailTransferFromInsufficientBalance() public {
        address from = MARKET;

        token.mint(from, 0.9e18);

        vm.prank(from);
        token.approve(address(this), 1e18);

        token.transferFrom(from, address(0xBEEF), 1e18);
    }

    function testMint(address from, uint256 amount) public {
        token.grantRole(TRANSFER_ROLE, from);
        token.mint(from, amount);

        assertEq(token.totalSupply(), amount);
        assertEq(token.balanceOf(from), amount);
    }

    function testBurn(
        address from,
        uint256 mintAmount,
        uint256 burnAmount
    ) public {
        vm.assume(from != address(0));
        burnAmount = bound(burnAmount, 0, mintAmount);

        token.grantRole(TRANSFER_ROLE, from);
        token.grantRole(BURNER_ROLE, from);

        token.mint(from, mintAmount);
        vm.prank(from);
        token.burn(burnAmount);

        assertEq(token.totalSupply(), mintAmount - burnAmount);
        assertEq(token.balanceOf(from), mintAmount - burnAmount);
    }

    function testApprove(address to, uint256 amount) public {
        assertTrue(token.approve(to, amount));

        assertEq(token.allowance(address(this), to), amount);
    }

    function testTransfer(address from, uint256 amount) public {
        vm.assume(from != address(0));
        token.mint(address(this), amount);

        assertTrue(token.transfer(from, amount));
        assertEq(token.totalSupply(), amount);

        if (address(this) == from) {
            assertEq(token.balanceOf(address(this)), amount);
        } else {
            assertEq(token.balanceOf(address(this)), 0);
            assertEq(token.balanceOf(from), amount);
        }
    }

    function testTransferFrom(
        address to,
        uint256 approval,
        uint256 amount
    ) public {
        vm.assume(to != address(0));
        amount = bound(amount, 0, approval);

        address from = MARKET;

        token.mint(from, amount);

        vm.prank(from);
        token.approve(address(this), approval);

        assertTrue(token.transferFrom(from, to, amount));
        assertEq(token.totalSupply(), amount);

        uint256 app = from == address(this) || approval == type(uint256).max ? approval : approval - amount;
        assertEq(token.allowance(from, address(this)), app);

        if (from == to) {
            assertEq(token.balanceOf(from), amount);
        } else {
            assertEq(token.balanceOf(from), 0);
            assertEq(token.balanceOf(to), amount);
        }
    }

    function testFailBurnInsufficientBalance(
        address to,
        uint256 mintAmount,
        uint256 burnAmount
    ) public {
        burnAmount = bound(burnAmount, mintAmount + 1, type(uint256).max);

        token.grantRole(TRANSFER_ROLE, to);
        token.grantRole(BURNER_ROLE, to);

        token.mint(to, mintAmount);
        vm.prank(to);
        token.burn(burnAmount);
    }

    function testFailTransferInsufficientBalance(
        address to,
        uint256 mintAmount,
        uint256 sendAmount
    ) public {
        sendAmount = bound(sendAmount, mintAmount + 1, type(uint256).max);

        token.mint(address(this), mintAmount);
        token.transfer(to, sendAmount);
    }

    function testFailTransferFromInsufficientAllowance(
        address to,
        uint256 approval,
        uint256 amount
    ) public {
        amount = bound(amount, approval + 1, type(uint256).max);

        address from = MARKET;

        token.mint(from, amount);

        vm.prank(from);
        token.approve(address(this), approval);

        token.transferFrom(from, to, amount);
    }

    function testFailTransferFromInsufficientBalance(
        address to,
        uint256 mintAmount,
        uint256 sendAmount
    ) public {
        sendAmount = bound(sendAmount, mintAmount + 1, type(uint256).max);

        address from = MARKET;

        token.mint(from, mintAmount);

        vm.prank(from);
        token.approve(address(this), sendAmount);

        token.transferFrom(from, to, sendAmount);
    }
}
