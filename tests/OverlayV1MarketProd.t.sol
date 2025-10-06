// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {OverlayV1Deployer} from "contracts/OverlayV1Deployer.sol";
import {Position} from "contracts/libraries/Position.sol";

contract MarketProdTest is Test {
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

    OverlayV1Token ovl = OverlayV1Token(0x1F34c87ded863Fe3A3Cd76FAc8adA9608137C8c3);
    OverlayV1Market market = OverlayV1Market(0x799B52DF5394b143C7786b1E6E4533CE1De5D817);

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC"), 58788406);
    }

    // Test pausable markets

    function testLiquidateProd() public {
        vm.startPrank(0xc65055B095079244E0f0232AfaD3d3699Ac3EdbA);
        market.liquidate(0xeB497c228F130BD91E7F13f81c312243961d894A, 32);
    }
}
