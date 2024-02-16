// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {IOverlayV1Token} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {OverlayV1FeedFactoryMock} from "../../contracts/mocks/OverlayV1FeedFactoryMock.sol";
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
contract RiskParamAnalysisFork is Test {
    OverlayV1Factory factory;
    address feed;
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
        feed = market.feed();

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
            "isLong", ";",
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
        _analyzeRiskPnl({
            param: Risk.Parameters(idx),
            paramName: marketParamsNames[idx],
            outPath: "pnl_single.csv",
            fromValue: fromValue,
            toValue: toValue,
            step: (toValue - fromValue) / steps
        });
    }

    function _analyzeRiskPnl(
        Risk.Parameters param,
        string memory paramName,
        string memory outPath,
        uint256 fromValue,
        uint256 toValue,
        uint256 step
    ) internal {
        // build options
        uint256 collateral = 10e18;
        uint256 leverage = 1e18;
        bool isLong = true;

        // compute pnl by building and unwinding a position
        for (uint256 paramValue = fromValue; paramValue <= toValue; paramValue += step) {
            // reset market
            _resetMarket();

            // update risk param
            vm.prank(GOVERNOR);
            factory.setRiskParam(feed, param, paramValue);

            // get OV balance before
            uint256 ovBalanceBefore = ovl.balanceOf(address(this));

            // build a position
            uint256 posId = market.build({
                collateral: collateral,
                leverage: leverage,
                isLong: isLong,
                priceLimit: type(uint256).max
            });

            // unwind the whole position
            market.unwind(posId, 1e18, 0);

            // compute pnl
            int256 pnl = int256(ovl.balanceOf(address(this))) - int256(ovBalanceBefore);

            string memory line = string(abi.encodePacked(
                paramName, ";",
                vm.toString(paramValue), ";",
                vm.toString(collateral), ";",
                vm.toString(leverage), ";",
                vm.toString(isLong), ";",
                vm.toString(pnl)
            ));

            vm.writeLine(outPath, line);

            if (step == 0) break; // avoid infinite loop
        }
    }

    function _resetMarket() internal {
        // create a new fork, since each one has its own state
        vm.createSelectFork(vm.envString("SEPOLIA_PROVIDER_URL"), 14594566);
        // deal ovl token
        deal(address(ovl), address(this), 8_000_000e18);
        ovl.approve(address(market), type(uint256).max);
    }
}