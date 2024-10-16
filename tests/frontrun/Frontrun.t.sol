// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {Test, console2} from "forge-std/Test.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1Token} from "contracts/OverlayV1Token.sol";
import {AggregatorMock} from "contracts/mocks/AggregatorMock.sol";
import {OverlayV1ChainlinkFeed} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import {OverlayV1ChainlinkFeedFactory} from
    "contracts/feeds/chainlink/OverlayV1ChainlinkFeedFactory.sol";
import "contracts/libraries/Oracle.sol";

contract FrontrunTest is Test {
    bytes32 constant ADMIN_ROLE = 0x00;
    bytes32 constant MINTER_ROLE = keccak256("MINTER");
    bytes32 constant GOVERNOR_ROLE = keccak256("GOVERNOR");

    address immutable GOVERNOR = makeAddr("governor");
    address immutable FEE_RECIPIENT = makeAddr("fee-recipient");
    address immutable USER = makeAddr("user");
    address immutable USER1 = makeAddr("user1");

    uint8 immutable BLOCK_TIME_MULTIPLIER = 10;

    function append(string memory a, string memory b) internal pure returns (string memory) {
        return string(abi.encodePacked(a, b));
    }

    struct JsonConfig {
        // Blockchain's block time times 10. Ethereum = 120, Arbitrum = 2.
        // We have to multiple by ten so we can save precision.
        uint256 blockTime;
        uint256 frontrunCollateral;
        uint256 frontrunLeverage;
        uint256 initialBalance;
        uint256 initialCollateral;
        uint256 initialLeverage;
        uint256 initialPrice;
        uint256 priceSpike;
        uint256 waitTime;
    }

    JsonConfig config;

    OverlayV1Token ov;
    OverlayV1Factory marketFactory;
    OverlayV1Market market;

    AggregatorMock aggregator;
    AggregatorMock sequencerOracle;
    OverlayV1ChainlinkFeedFactory feedFactory;
    OverlayV1ChainlinkFeed feed;

    function setUp() public {
        setUpConfig();

        vm.writeFile("tests/frontrun/frontrun_results.csv", "waitTimeToUnwind,profit,priceOverMicroWindow,priceOverMacroWindow\n");

        ov = new OverlayV1Token();

        ov.grantRole(ADMIN_ROLE, GOVERNOR);
        ov.grantRole(MINTER_ROLE, GOVERNOR);
        ov.grantRole(GOVERNOR_ROLE, GOVERNOR);

        vm.prank(GOVERNOR);
        ov.mint(USER, 100e18);

        setUpSequencerOracle();
        setUpChainlinkFeed();
        setUpMarket();
    }

    function testFuzz_FrontrunAttempt(uint256 waitTimeToUnwind) public {
        // Limit waitTimeToUnwind values from 1 to 500
        waitTimeToUnwind = bound(waitTimeToUnwind, 1, 1000);

        // Initialize market with two positions
        vm.startPrank(USER);
        ov.approve(address(market), type(uint256).max);
        // One is long
        market.build(config.initialCollateral, config.initialLeverage, true, type(uint256).max);
        // Another is short
        market.build(config.initialCollateral, config.initialLeverage, false, 0);
        vm.stopPrank();

        // Set up USER1 for frontrunning
        vm.prank(GOVERNOR);
        ov.mint(USER1, config.initialBalance);
        uint256 initialBalance = ov.balanceOf(USER1);

        // Price spike
        uint80 currentRoundId = aggregator.latestRoundId();
        updateAggregatorPrice(currentRoundId + 1, config.priceSpike);

        // Frontrunner builds a long position
        vm.startPrank(USER1);
        ov.approve(address(market), type(uint256).max);
        uint256 positionId = market.build(
            config.frontrunCollateral, config.frontrunLeverage, true, type(uint256).max
        );
        uint256 buildTimestamp = block.timestamp;
        uint256 buildBlock = block.number;
        vm.stopPrank();

        if (waitTimeToUnwind > config.waitTime) {
            // Wait for specified time
            vm.warp(block.timestamp + config.waitTime);
            vm.roll(block.number + config.waitTime * BLOCK_TIME_MULTIPLIER / config.blockTime);

            // Price returns back to normal
            updateAggregatorPrice(aggregator.latestRoundId() + 1, config.initialPrice);
        }

        // Wait `waitTimeToUnwind`
        vm.warp(buildTimestamp + waitTimeToUnwind);
        vm.roll(buildBlock + waitTimeToUnwind * BLOCK_TIME_MULTIPLIER / config.blockTime);

        // Update the price again to not get `stale price`
        updateAggregatorPrice(aggregator.latestRoundId() + 1, config.initialPrice);

        // Unwind
        vm.prank(USER1);
        market.unwind(positionId, 1e18, 0);

        Oracle.Data memory data2 = feed.latest();
        console2.log("priceOverMicroWindow", int256(data2.priceOverMicroWindow));
        console2.log("priceOverMacroWindow", int256(data2.priceOverMacroWindow));

        // Profit
        uint256 finalBalance = ov.balanceOf(USER1);
        int256 profit = int256(finalBalance) - int256(initialBalance);

        console2.log("Unwound at block time:", block.timestamp);
        console2.log("Profit:", profit);

        // Write data into `frontrun_results.csv`
        writeDataToCSV(waitTimeToUnwind, profit);
    }

    function writeDataToCSV(uint256 waitTimeToUnwind, int256 profit) internal {
        Oracle.Data memory data = feed.latest();
        string memory csvLine =
            string(abi.encodePacked(vm.toString(waitTimeToUnwind), ",", vm.toString(profit), ",", vm.toString(data.priceOverMicroWindow), ",", vm.toString(data.priceOverMacroWindow)));
        vm.writeLine("tests/frontrun/frontrun_results.csv", csvLine);
    }

    function setUpMarket() private {
        marketFactory =
            new OverlayV1Factory(address(ov), FEE_RECIPIENT, address(sequencerOracle), 0);
        ov.grantRole(ADMIN_ROLE, address(marketFactory));

        // Params are extracted from `scripts/Create.s.sol`
        uint256[15] memory params;
        params[0] = 122000000000; // k
        params[1] = 500000000000000000; // lmbda
        params[2] = 2500000000000000; // delta
        params[3] = 50000000000000000000; // capPayoff
        params[4] = 8e23; // capNotional
        params[5] = 5000000000000000000; // capLeverage
        params[6] = 2592000; // circuitBreakerWindow
        params[7] = 66670000000000000000000; // circuitBreakerMintTarget
        params[8] = 100000000000000000; // maintenanceMargin
        params[9] = 100000000000000000; // maintenanceMarginBurnRate
        params[10] = 50000000000000000; // liquidationFeeRate
        params[11] = 750000000000000; // tradingFeeRate
        params[12] = 1e14; // minCollateral
        params[13] = 25000000000000; // priceDriftUpperLimit
        params[14] = 250; // averageBlockTime

        vm.startPrank(GOVERNOR);
        marketFactory.addFeedFactory(address(feedFactory));

        market = OverlayV1Market(
            marketFactory.deployMarket(address(feedFactory), address(feed), params)
        );
    }

    function setUpSequencerOracle() private {
        sequencerOracle = new AggregatorMock();
        sequencerOracle.setData(0, 0);
    }

    function setUpChainlinkFeed() private {
        aggregator = new AggregatorMock();
        setupInitialPrices();

        feedFactory = new OverlayV1ChainlinkFeedFactory(address(ov), 600, 3600);
        feed = OverlayV1ChainlinkFeed(feedFactory.deployFeed(address(aggregator), 120 minutes));
        ov.grantRole(GOVERNOR_ROLE, GOVERNOR);
    }

    function setupInitialPrices() private {
        for (uint80 i = 0; i < 5; i++) {
            updateAggregatorPrice(i, config.initialPrice);
            vm.warp(block.timestamp + 30 minutes);
        }
    }

    function updateAggregatorPrice(uint80 roundId, uint256 price) private {
        aggregator.setData(roundId, int256(price));
        vm.roll(block.number + 1);
        vm.warp(block.timestamp + 1);
    }

    function setUpConfig() private {
        string memory root = vm.projectRoot();
        string memory path = append(root, "/config/frontrun.json");
        string memory json = vm.readFile(path);
        bytes memory jsonBytes = vm.parseJson(json);

        config = abi.decode(jsonBytes, (JsonConfig));
    }
}
