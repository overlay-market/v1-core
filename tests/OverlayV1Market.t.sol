// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {OverlayV1Deployer} from "contracts/OverlayV1Deployer.sol";
import {Position} from "contracts/libraries/Position.sol";

contract MarketTest is Test {
    bytes32 constant ADMIN = 0x00;
    bytes32 constant MINTER_ROLE = keccak256("MINTER");
    bytes32 constant BURNER_ROLE = keccak256("BURNER");
    bytes32 constant GOVERNOR_ROLE = keccak256("GOVERNOR");
    bytes32 constant GUARDIAN_ROLE = keccak256("GUARDIAN");
    bytes32 constant PAUSER_ROLE = keccak256("PAUSER");

    address immutable GOVERNOR = makeAddr("governor");
    address immutable FEE_RECIPIENT = makeAddr("fee-recipient");
    address immutable PAUSER = makeAddr("pauser");
    address immutable USER = makeAddr("user");
    address constant FEED_FACTORY = 0x92ee7A26Dbc18E9C0157831d79C2906A02fD1FAe;
    address constant FEED = 0x46B4143CAf2fE2965349FCa53730e83f91247E2C;

    OverlayV1Token ov;
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Deployer deployer;

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC"), 169_490_320);
        ov = new OverlayV1Token();
        factory = new OverlayV1Factory(address(ov), FEE_RECIPIENT);

        ov.grantRole(ADMIN, address(factory));
        ov.grantRole(ADMIN, GOVERNOR);
        ov.grantRole(MINTER_ROLE, GOVERNOR);
        ov.grantRole(GOVERNOR_ROLE, GOVERNOR);
        ov.grantRole(PAUSER_ROLE, PAUSER);

        uint256[15] memory params;
        params[0] = uint256(0x0000000000000000000000000000000000000000000000000000001af2af8c84);
        params[1] = uint256(0x0000000000000000000000000000000000000000000000000a688906bd8b0000);
        params[2] = uint256(0x0000000000000000000000000000000000000000000000000008caffd7d1b000);
        params[3] = uint256(0x0000000000000000000000000000000000000000000000004563918244f40000);
        params[4] = uint256(0x00000000000000000000000000000000000000000000043c33c1937564800000);
        params[5] = uint256(0x0000000000000000000000000000000000000000000000008ac7230489e80000);
        params[6] = uint256(0x0000000000000000000000000000000000000000000000000000000000278d00);
        params[7] = uint256(0x00000000000000000000000000000000000000000000005a59a576f4730aaaaa);
        params[8] = uint256(0x000000000000000000000000000000000000000000000000008e1bc9bf040000);
        params[9] = uint256(0x00000000000000000000000000000000000000000000000000b1a2bc2ec50000);
        params[10] = uint256(0x00000000000000000000000000000000000000000000000000b1a2bc2ec50000);
        params[11] = uint256(0x0000000000000000000000000000000000000000000000000002aa1efb94e000);
        params[12] = uint256(0x00000000000000000000000000000000000000000000000000005af3107a4000);
        params[13] = uint256(0x00000000000000000000000000000000000000000000000000004f2044187000);
        params[14] = uint256(0x0000000000000000000000000000000000000000000000000000000000000000);

        vm.startPrank(GOVERNOR);
        factory.addFeedFactory(FEED_FACTORY);

        market = OverlayV1Market(factory.deployMarket(FEED_FACTORY, FEED, params));

        ov.mint(USER, 100e18);
    }

    // Test pausable markets

    function testPause() public {
        vm.startPrank(USER);
        ov.approve(address(market), type(uint256).max);
        // Build postion 0
        market.build(1e18, 1e18, true, type(uint256).max);
        // Build postion 1
        market.build(1e18, 1e18, true, type(uint256).max);
        // Unwind postion 0
        market.unwind(0, 1e18, 0);

        vm.startPrank(PAUSER);
        factory.pause(FEED);

        vm.startPrank(USER);
        vm.expectRevert("Pausable: paused");
        market.build(1e18, 1e18, true, type(uint256).max);
        vm.expectRevert("Pausable: paused");
        market.unwind(1, 1e18, 0);
        vm.expectRevert("Pausable: paused");
        market.liquidate(USER, 1);

        vm.startPrank(PAUSER);

        factory.unpause(FEED);

        vm.startPrank(USER);
        market.build(1e18, 1e18, true, type(uint256).max);
        market.unwind(1, 1e18, 0);
    }

    function testRoles() public {
        vm.startPrank(USER);
        vm.expectRevert();
        factory.pause(FEED);

        vm.startPrank(GOVERNOR);
        vm.expectRevert();
        factory.pause(FEED);

        vm.startPrank(PAUSER);
        factory.pause(FEED);

        vm.startPrank(USER);
        vm.expectRevert();
        factory.unpause(FEED);

        vm.startPrank(GOVERNOR);
        vm.expectRevert();
        factory.unpause(FEED);

        vm.startPrank(PAUSER);
        factory.unpause(FEED);
    }

    // Test shutdown markets

    function testShutdown(uint256 _fraction) public {
        _fraction = bound(_fraction, 1e14, 9999e14);

        vm.startPrank(USER);
        
        ov.approve(address(market), type(uint256).max);
        // Build postion 0
        market.build(1e18, 1e18, true, type(uint256).max);
        // Build postion 1
        market.build(1e18, 1e18, true, type(uint256).max);
        // Build postion 2
        market.build(1e18, 1e18, true, type(uint256).max);
        // Unwind postion 0
        market.unwind(0, 1e18, 0);
        // Unwind _fraction of postion 1
        market.unwind(1, _fraction, 0);

        vm.expectRevert("OVV1: !shutdown");
        market.emergencyWithdraw(1);

        vm.startPrank(GOVERNOR);
        vm.expectRevert("OVV1: !guardian");
        factory.shutdown(FEED);

        ov.grantRole(GUARDIAN_ROLE, GOVERNOR);
        factory.shutdown(FEED);

        vm.startPrank(USER);
        vm.expectRevert("OVV1: shutdown");
        market.build(1e18, 1e18, true, type(uint256).max);
        vm.expectRevert("OVV1: shutdown");
        market.unwind(1, 1e18, 0);
        vm.expectRevert("OVV1: shutdown");
        market.liquidate(USER, 1);

        uint256 balanceBefore = ov.balanceOf(USER);
        (uint96 notionalInitial,,,,,,,uint16 fractionRemaining) = market.positions(keccak256(abi.encodePacked(USER, uint256(1))));
        market.emergencyWithdraw(1);
        assertEq(balanceBefore + notionalInitial*fractionRemaining/1e4, ov.balanceOf(USER));
        balanceBefore = ov.balanceOf(USER);
        (notionalInitial,,,,,,,fractionRemaining) = market.positions(keccak256(abi.encodePacked(USER, uint256(2))));
        market.emergencyWithdraw(2);
        assertEq(balanceBefore + notionalInitial*fractionRemaining/1e4, ov.balanceOf(USER));
        
        assertEq(ov.balanceOf(address(market)), 0);
    }
}
