// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Cast} from "./Cast.sol";
import {PropertiesAsserts} from "./Helper.sol";

// Run with medusa fuzz --target ./CastTest.sol --deployment-order CastTest

contract CastTest is PropertiesAsserts {
    function testToUint32Bounded(uint256 x) public {
        assertGte(x, Cast.toUint32Bounded(x), "x should be greater than or equal to Cast.toUint32Bounded(x)");
    }

    function testToInt192Bounded(int256 x) public {
        if (x >= type(int192).min) {
            assertGte(x, Cast.toInt192Bounded(x), "x should be greater than or equal to Cast.toInt192Bounded(x)");
        }

        if (x <= type(int192).max) {
            assertLte(x, Cast.toInt192Bounded(x), "x should be less than or equal to Cast.toInt192Bounded(x)");
        }
    }
}
