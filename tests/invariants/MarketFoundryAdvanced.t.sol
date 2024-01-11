// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "./MarketFoundry.t.sol";

// run from base project directory with:
// forge test --mc MarketFoundryAdvanced
//
// get coverage report (see https://medium.com/@rohanzarathustra/forge-coverage-overview-744d967e112f):
// 1) forge coverage --report lcov --report-file tests/invariants/coverage-foundry-advanced.lcov --mc MarketFoundryAdvanced
// 2) genhtml tests/invariants/coverage-foundry-advanced.lcov -o tests/invariants/coverage-foundry-advanced
// 3) open tests/invariants/coverage-foundry-advanced/index.html in your browser and
//    navigate to the relevant source file to see line-by-line execution records
contract MarketFoundryAdvanced is MarketFoundry {

    function setUp() public override {
        // call parent first to setup test environment
        super.setUp();

        // advanced test with guiding of the fuzzer
        //
        // make this contract into a handler to wrap the market's build()
        // function and instruct foundry on how to call it.
        //  This significantly reduces the amount of useless fuzz runs
        targetContract(address(this));

        // functions to target during invariant tests
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = this.buildWrapper.selector;

        targetSelector(FuzzSelector({
            addr: address(this),
            selectors: selectors
        }));
    }

    // wrapper around market.build() to "guide" the fuzz test
    function buildWrapper(bool isLong, uint256 collateral) public {
        // bound collateral to avoid reverts
        collateral = TestUtils.clampBetween(collateral, MIN_COLLATERAL, CAP_NOTIONAL);

        // target senders are configured to be ALICE or BOB in `super.setUp()`
        vm.prank(msg.sender);

        market.build({
            collateral: collateral,
            leverage: 1e18,
            isLong: isLong,
            priceLimit: isLong ? type(uint256).max : 0
        });
    }

    // invariants inherited from base contract
}
