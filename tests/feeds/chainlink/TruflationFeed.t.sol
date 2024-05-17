pragma solidity 0.8.10;

import "forge-std/StdJson.sol";
import {Test, console2} from "forge-std/Test.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "../../../contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";
import "../../../contracts/libraries/Oracle.sol";

contract TruflationFeedTest is Test {
    using Oracle for Oracle.Data;
    using stdJson for string;

    function append(string memory a, string memory b) internal pure returns (string memory) {
        return string(abi.encodePacked(a, b));
    }

    struct JsonConfig {
        uint256 answerValueCeiling;
        uint256 answerValueFloor;
        uint64 blockNumber;
        address feedAddress;
        uint256 heartbeat;
        uint256 macroWindowCeiling;
        uint256 macroWindowFloor;
        uint256 microWindowCeiling;
        uint256 microWindowFloor;
        uint8 roundCount;
    }

    string truflationRPC;
    JsonConfig config;
    AggregatorV3Interface feed;

    function setUp() public {
        string memory root = vm.projectRoot();
        string memory path = append(root, "/config/truflationFeed.json");
        string memory json = vm.readFile(path);
        bytes memory jsonBytes = json.parseRaw("");

        config = abi.decode(jsonBytes, (JsonConfig));
        feed = AggregatorV3Interface(config.feedAddress);

        truflationRPC = vm.envString("TRUFLATION_RPC");
        vm.createSelectFork(truflationRPC, config.blockNumber);
    }

    function test_ConsecutiveRoundId() public {
        (uint80 latestRoundId,,,,) = feed.latestRoundData();
        uint256 updatedAt;
        uint256 previousUpdatedAt = type(uint256).max;

        for (uint80 index = latestRoundId; index > latestRoundId - config.roundCount; index--) {
            (,,, updatedAt,) = feed.getRoundData(index);

            assertLe(updatedAt, previousUpdatedAt);
            previousUpdatedAt = updatedAt;
        }
    }

    function test_AnswerValue() public {
        (uint80 latestRoundId,,,,) = feed.latestRoundData();

        for (uint80 index = latestRoundId; index > latestRoundId - config.roundCount; index--) {
            (,,, uint256 answer,) = feed.getRoundData(index);

            assertGt(answer, config.answerValueFloor);
            assertLt(answer, config.answerValueCeiling);
        }
    }

    // we check last n rounds and see if timestamps are not bigger than the current block.timestamp
    function test_TimestampsInSeconds() public {
        (uint80 latestRoundId,,,,) = feed.latestRoundData();
        uint256 updatedAt;
        uint256 startedAt;

        for (uint80 index = latestRoundId; index > latestRoundId - config.roundCount; index--) {
            (,, startedAt, updatedAt,) = feed.getRoundData(index);

            int256 updatedAtDiff = int256(block.timestamp) - int256(updatedAt);
            int256 startedAtDiff = int256(block.timestamp) - int256(startedAt);

            assertGt(updatedAtDiff, 0);
            assertGt(startedAtDiff, 0);
        }
    }

    function test_Heartbeat() public {
        (uint80 latestRoundId,,,,) = feed.latestRoundData();
        uint256 updatedAt;
        uint256 previousUpdatedAt = block.timestamp;

        for (uint80 index = latestRoundId; index > latestRoundId - config.roundCount; index--) {
            (,,, updatedAt,) = feed.getRoundData(index);

            assertLt(previousUpdatedAt - updatedAt, config.heartbeat);
            previousUpdatedAt = updatedAt;
        }
    }

    function test_AnsweredInRoundCompatability() public {
        (uint80 latestRoundId,,,,) = feed.latestRoundData();
        uint256 answeredInRound;

        for (uint80 index = latestRoundId; index > latestRoundId - config.roundCount; index--) {
            (,,,, answeredInRound) = feed.getRoundData(index);

            uint80 expectedAnsweredInRound = uint80(answeredInRound);
            assertEq(answeredInRound, expectedAnsweredInRound);
        }
    }

    function test_TWAP() public {
        for (uint80 index = 0; index < config.roundCount; index++) {
            vm.createSelectFork(truflationRPC, config.blockNumber - index);

            OverlayV1ChainlinkFeed wrappedFeed = new OverlayV1ChainlinkFeed(
                address(0), config.feedAddress, 600, 3600, config.heartbeat
            );

            Oracle.Data memory data = wrappedFeed.latest();

            console2.log("Price over macro window: ", data.priceOverMacroWindow);
            console2.log("Price over micro window: ", data.priceOverMicroWindow);

            assertGt(data.priceOverMicroWindow, config.microWindowFloor);
            assertLt(data.priceOverMicroWindow, config.microWindowCeiling);
            assertGt(data.priceOverMacroWindow, config.macroWindowFloor);
            assertLt(data.priceOverMacroWindow, config.macroWindowCeiling);
        }
    }
}
