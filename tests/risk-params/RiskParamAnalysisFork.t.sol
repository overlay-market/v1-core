// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {IOverlayV1Token} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {IOverlayV1Feed} from "../../contracts/interfaces/feeds/IOverlayV1Feed.sol";
import {Oracle} from "../../contracts/libraries/Oracle.sol";
import {GOVERNOR_ROLE, MINTER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {Risk} from "../../contracts/libraries/Risk.sol";

/// @notice Creates a `pnl.csv` [and `pnl_single.csv`] file with the following columns:
/// param_name;param_value;collateral;leverage;isLong;pnl
/// @dev run with `PRINT_PNL=true forge test -vvv --mc RiskParamAnalysisFork`
/// @dev the following env variables have to be set for the test to run:
/// - SEPOLIA_PROVIDER_URL: the url of the sepolia rpc provider
/// - MARKET_ADDRESS: the address of the market contract to test
/// @dev the following env variables have to be set to analyze a single parameter in detail:
/// - PARAM_INDEX: the index of the parameter to test
/// - FROM_VALUE: the starting value of the parameter
/// - TO_VALUE: the ending value of the parameter
/// - STEPS: the number of steps to take between `FROM_VALUE` and `TO_VALUE`
/// @dev the following are optional env variables that apply for both tests:
/// - REMOVE_FEES: boolean to indicate to change fee recipient to this account to remove the incidence of fees
/// - TIME_BEFORE_UNWIND: seconds to wait in between building and unwinding a position
/// - PRICE_MOVE_PERCENT: percentage to move the price by (eg. -5 to decrease by 5%) between building and unwinding a position
contract RiskParamAnalysisFork is Test {
    OverlayV1Factory factory;
    IOverlayV1Feed feed;
    OverlayV1Market market;
    IOverlayV1Token ovl;

    address constant GOVERNOR = 0xc946446711eE82b87cc34611810B0f2DD14c15DD;

    string[15] marketParamsNames = [
        "K",
        "Lmbda",
        "Delta",
        "CapPayoff",
        "CapNotional",
        "CapLeverage",
        "CircuitBreakerWindow",
        "CircuitBreakerMintTarget",
        "MaintenanceMargin",
        "MaintenanceMarginBurnRate",
        "LiquidationFeeRate",
        "TradingFeeRate",
        "MinCollateral",
        "PriceDriftUpperLimit",
        "AverageBlockTime"
    ];

    function setUp() public virtual {
        // create a fork of the blockchain
        vm.createSelectFork(vm.envString("SEPOLIA_PROVIDER_URL"), 14594566);

        // attach deployed contracts
        market = OverlayV1Market(vm.envAddress("MARKET_ADDRESS"));
        (, bytes memory data) = address(market).call(abi.encodeWithSignature("ovl()"));
        ovl = IOverlayV1Token(abi.decode(data, (address)));
        factory = OverlayV1Factory(market.factory());
        feed = IOverlayV1Feed(market.feed());

        // deal ovl token
        deal(address(ovl), address(this), 8_000_000e18);
        ovl.approve(address(market), type(uint256).max);

        // remove previous files
        try vm.removeFile("pnl.csv") {} catch {}
        try vm.removeFile("pnl_single.csv") {} catch {}

        // set the header line
        string memory line = string(abi.encodePacked(
            "param_name", ";",
            "param_value", ";",
            "collateral", ";",
            "leverage", ";",
            "is_long", ";",
            "seconds_elapsed", ";",
            "price_move_percent", ";",
            "pnl"
        ));
        
        bool printToFile = vm.envOr("PRINT_PNL", false);
        if (printToFile) vm.writeLine("pnl.csv", line);
        if (printToFile) vm.writeLine("pnl_single.csv", line);
    }

    function test() public {
        bool printToFile = vm.envOr("PRINT_PNL", false);
        // only run this test if we want to print to file
        if (!printToFile) return;

        for (uint256 i = 0; i < marketParamsNames.length; i++) {
            uint256 baseParamValue = market.params(i);
            uint256 fromValue = baseParamValue * 90 / 100; // 90% of the base value
            uint256 toValue = baseParamValue * 110 / 100;  // 110% of the base value
            uint256 step = (toValue - fromValue) / 9;      // 9 steps
            _analyzeRiskPnl({
                param: Risk.Parameters(i),
                paramName: marketParamsNames[i],
                outPath: "pnl.csv",
                fromValue: fromValue,
                toValue: toValue,
                step: step
            });
        }
    }

    function testSingleParam() public {
        bool printToFile = vm.envOr("PRINT_PNL", false);
        // only run this test if we want to print to file
        if (!printToFile) return;

        uint256 idx = vm.envUint("PARAM_INDEX");
        uint256 fromValue = vm.envUint("FROM_VALUE");
        uint256 toValue = vm.envUint("TO_VALUE");
        uint256 steps = vm.envUint("STEPS");
        for (uint256 i = 0; i <= 1; i++) {
            _analyzeRiskPnl({
                param: Risk.Parameters(idx),
                paramName: marketParamsNames[idx],
                outPath: "pnl_single.csv",
                fromValue: fromValue,
                toValue: toValue,
                step: (toValue - fromValue) / steps,
                fuzzCollateral: 3,
                isLong: i == 0 ? true : false
            });
        }
    }

    function _analyzeRiskPnl(
        Risk.Parameters param,
        string memory paramName,
        string memory outPath,
        uint256 fromValue,
        uint256 toValue,
        uint256 step
    ) internal {
        _analyzeRiskPnl(
            param,
            paramName,
            outPath,
            fromValue,
            toValue,
            step,
            1,
            true
        );
    }

    function _analyzeRiskPnl(
        Risk.Parameters param,
        string memory paramName,
        string memory outPath,
        uint256 fromValue,
        uint256 toValue,
        uint256 step,
        uint256 fuzzCollateral,
        bool isLong
    ) internal {
        // build options
        uint256 collateral = 10e18;
        uint256 leverage = 1e18;

        for (uint256 collateralMultiplier = 0; collateralMultiplier <= fuzzCollateral - 1; collateralMultiplier++) {
            // compute pnl by building and unwinding a position
            for (uint256 paramValue = fromValue; paramValue <= toValue; paramValue += step) {
                // reset market
                _resetMarket();

                // update risk param
                vm.prank(GOVERNOR);
                factory.setRiskParam(address(feed), param, paramValue);

                // get OV balance before
                uint256 ovBalanceBefore = ovl.balanceOf(address(this));

                // build a position
                uint256 posId = market.build({
                    collateral: collateral * (1 + collateralMultiplier),
                    leverage: leverage,
                    isLong: isLong,
                    priceLimit: isLong ? type(uint256).max : 0
                });

                // skip some time before unwindg to take funding payments into account
                skip(vm.envOr("TIME_BEFORE_UNWIND", uint256(0)));

                // move the price informed by the feed
                {
                    Oracle.Data memory data = feed.latest();
                    uint256 priceBefore = data.priceOverMacroWindow; // likely to be the same as `priceOverMicroWindow`
                    int256 priceMovement = vm.envOr("PRICE_MOVE_PERCENT", int256(0));
                    uint256 newPrice = priceBefore * (uint256(100 + priceMovement))/100;
                    data.priceOverMacroWindow = newPrice;
                    data.priceOverMicroWindow = newPrice;
                    data.priceOneMacroWindowAgo = newPrice;
                    vm.mockCall(
                        address(feed),
                        abi.encodeWithSelector(IOverlayV1Feed.latest.selector),
                        abi.encode(data)
                    );
                }

                // unwind the whole position
                market.unwind(posId, 1e18, isLong ? 0 : type(uint256).max);

                // compute pnl
                int256 pnl = int256(ovl.balanceOf(address(this))) - int256(ovBalanceBefore);

                string memory line = string(abi.encodePacked(
                    paramName, ";",
                    vm.toString(paramValue), ";",
                    vm.toString(collateral * (1 + collateralMultiplier)), ";", // collateral
                    vm.toString(leverage), ";",
                    vm.toString(isLong), ";",
                    vm.toString(vm.envOr("TIME_BEFORE_UNWIND", uint256(0))), ";", // seconds_elapsed
                    vm.toString(vm.envOr("PRICE_MOVE_PERCENT", int256(0))), ";", // price_move_percent
                    vm.toString(pnl)
                ));

                vm.writeLine(outPath, line);

                if (step == 0) break; // avoid infinite loop
            }
        }
    }

    function _resetMarket() internal {
        // clear mocked calls (eg. feed price)
        vm.clearMockedCalls();
        // create a new fork, since each one has its own state
        vm.createSelectFork(vm.envString("SEPOLIA_PROVIDER_URL"), 14594566);
        // deal ovl token
        deal(address(ovl), address(this), 8_000_000e18);
        ovl.approve(address(market), type(uint256).max);
        bool removeIncidenceOfFees = vm.envOr("REMOVE_FEES", false);
        if (removeIncidenceOfFees) {
            vm.prank(GOVERNOR);
            factory.setFeeRecipient(address(this));
        }
    }
}