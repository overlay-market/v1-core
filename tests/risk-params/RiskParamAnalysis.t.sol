// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

import {OverlayV1Factory} from "../../contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "../../contracts/OverlayV1Market.sol";
import {OverlayV1Token} from "../../contracts/OverlayV1Token.sol";
import {OverlayV1FeedFactoryMock} from "../../contracts/mocks/OverlayV1FeedFactoryMock.sol";
import {GOVERNOR_ROLE, MINTER_ROLE} from "../../contracts/interfaces/IOverlayV1Token.sol";
import {Risk} from "../../contracts/libraries/Risk.sol";

contract RiskParamAnalysis is Test {
    OverlayV1Factory factory;
    OverlayV1FeedFactoryMock feedFactory;
    address feed;
    OverlayV1Market market;
    OverlayV1Token ovl;

    uint256 ovlSupply = 8_000_000e18;
    uint256 marketResetCounter = 0;

    uint256[15] baseMarketParams = [
        uint256(122000000000), // k
        500000000000000000, // lmbda
        2500000000000000, // delta
        5000000000000000000, // capPayoff
        8e23, // capNotional
        5000000000000000000, // capLeverage
        2592000, // circuitBreakerWindow
        66670000000000000000000, // circuitBreakerMintTarget
        100000000000000000, // maintenanceMargin
        100000000000000000, // maintenanceMarginBurnRate
        50000000000000000, // liquidationFeeRate
        750000000000000, // tradingFeeRate
        1e14, // minCollateral
        25000000000000, // priceDriftUpperLimit
        1000 // averageBlockTime
    ];

    string[15] baseMarketParamsNames = [
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
        // deploy contracts
        ovl = new OverlayV1Token();
        factory = new OverlayV1Factory(address(ovl), address(0x111));
        // market will be later deployed by factory

        // ovl config
        ovl.grantRole(MINTER_ROLE, address(this));
        ovl.mint(address(this), ovlSupply);
        ovl.renounceRole(MINTER_ROLE, address(this));

        // factory config
        ovl.grantRole(GOVERNOR_ROLE, address(this));
        ovl.grantRole(bytes32(0x00), address(factory)); // grant admin role
        feedFactory = new OverlayV1FeedFactoryMock({_microWindow: 600, _macroWindow: 1800});
        factory.addFeedFactory(address(feedFactory));

        // market config and deployment
        feed = feedFactory.deployFeed({price: 1e18, reserve: 2_000_000e18});
        market = OverlayV1Market(factory.deployMarket(address(feedFactory), feed, baseMarketParams));
        ovl.approve(address(market), ovlSupply);

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
    /// @dev run `PRINT_PNL=true forge test -vvv --mc RiskParamAnalysis` to create the file.
    function test_runAnalysis() public {
        for (uint256 i = 0; i < baseMarketParams.length; i++) {
            _analyzeRiskPnl(Risk.Parameters(i), baseMarketParamsNames[i], int256(baseMarketParams[i]));
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

            bool printToFile = vm.envOr("PRINT_PNL", false);
            if (printToFile) vm.writeLine("pnl.csv", line);
        }
    }

    function _resetMarket() internal {
        // deploy a different feed for each market to avoid reverts
        feed = feedFactory.deployFeed({price: 1e18 + ++marketResetCounter, reserve: 2_000_000e18});
        market = OverlayV1Market(factory.deployMarket(address(feedFactory), feed, baseMarketParams));
        ovl.approve(address(market), ovlSupply);
    }
}