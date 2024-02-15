// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {IOverlayV1Token} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {OverlayV1FeedFactoryMock} from "../../contracts/mocks/OverlayV1FeedFactoryMock.sol";
import {GOVERNOR_ROLE, MINTER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {Risk} from "../../contracts/libraries/Risk.sol";

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
    }

    /// @notice Creates a `pnl.csv` file with the following columns:
    /// TradingFeeRate;pnl
    /// @dev run `PRINT_PNL=true forge test -vvv --mc RiskParamAnalysisFork` to create the file.
    function test() public {
        bool printToFile = vm.envOr("PRINT_PNL", false);
        // only run this test if we want to print to file
        if (!printToFile) return;

        for (uint256 i = 0; i < marketParamsNames.length; i++) {
            _analyzeRiskPnl(Risk.Parameters(i), marketParamsNames[i], int256(market.params(i)));
        }
    }

    function _analyzeRiskPnl(Risk.Parameters param, string memory paramName, int256 baseParamValue) internal {
        // build options
        uint256 collateral = 10e18;
        uint256 leverage = 1e18;
        bool isLong = true;

        // compute pnl by building and unwinding a position
        int256 step = baseParamValue * 25 / 1000; // 2.5% step
        // analyze 4 steps up and 4 steps down from `baseParamValue`
        for (int256 i = -4; i <= 4; i++) {
            // reset market
            _resetMarket();

            // update risk param
            uint256 paramValue = uint256(baseParamValue + i * step);
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

            vm.writeLine("pnl.csv", line);
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