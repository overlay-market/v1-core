// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {OverlayV1Deployer} from "contracts/OverlayV1Deployer.sol";
import {Position} from "contracts/libraries/Position.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";

contract SequencerTest is Test {
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
    AggregatorMock sequencer_oracle;

    OverlayV1Token ov;
    OverlayV1Factory factory;
    OverlayV1Market market;
    OverlayV1Deployer deployer;

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC"), 169_490_320);
        ov = new OverlayV1Token();
        sequencer_oracle = new AggregatorMock();
        factory =
            new OverlayV1Factory(address(ov), FEE_RECIPIENT, address(sequencer_oracle), 30 minutes);

        ov.grantRole(ADMIN, address(factory));
        ov.grantRole(ADMIN, GOVERNOR);
        ov.grantRole(MINTER_ROLE, GOVERNOR);
        ov.grantRole(GOVERNOR_ROLE, GOVERNOR);
        ov.grantRole(PAUSER_ROLE, PAUSER);

        uint256[15] memory params;
        params[0] = 115740740740;
        params[1] = 750000000000000000;
        params[2] = 2475000000000000;
        params[3] = 5000000000000000000;
        params[4] = 20000000000000000000000;
        params[5] = 10000000000000000000;
        params[6] = 2592000;
        params[7] = 1666666666666666666666;
        params[8] = 40000000000000000;
        params[9] = 50000000000000000;
        params[10] = 50000000000000000;
        params[11] = 750000000000000;
        params[12] = 100000000000000;
        params[13] = 87000000000000;
        params[14] = 250;

        vm.startPrank(GOVERNOR);
        factory.addFeedFactory(FEED_FACTORY);

        market = OverlayV1Market(factory.deployMarket(FEED_FACTORY, FEED, params));

        ov.mint(USER, 100e18);
    }

    function testSequencerDown() public {
        sequencer_oracle.setData(1, 1); //Sequencer Down
        vm.startPrank(USER);
        ov.approve(address(market), type(uint256).max);
        vm.expectRevert("OVV1:!sequencer");
        market.build(1e18, 1e18, true, type(uint256).max);

        vm.stopPrank();
        sequencer_oracle.setData(2, 0); //Sequencer Up
        skip(15 minutes);

        vm.startPrank(USER);
        vm.expectRevert(); // Grace period not over
        market.build(1e18, 1e18, true, type(uint256).max);

        skip(45 minutes);
        market.build(1e18, 1e18, true, type(uint256).max);

        vm.stopPrank();
        sequencer_oracle.setData(3, 1); //Sequencer Down
        skip(60 minutes);

        vm.startPrank(USER);
        vm.expectRevert();
        market.unwind(0, 1e18, 0);

        vm.stopPrank();
        sequencer_oracle.setData(4, 0);
        skip(60 minutes);

        vm.startPrank(USER);
        market.unwind(0, 1e18, 0);

        assertLt(ov.balanceOf(USER), 100e18);
    }
}
