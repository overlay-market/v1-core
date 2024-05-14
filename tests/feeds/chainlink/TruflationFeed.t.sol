pragma solidity 0.8.10;

import "forge-std/StdJson.sol";
import {Test, console2} from "forge-std/Test.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TruflationFeedTest is Test {
    using stdJson for string;

    function append(string memory a, string memory b) internal pure returns (string memory) {
        return string(abi.encodePacked(a, b));
    }

    struct JsonConfig {
        address feedAddress;
        uint256 heartbeat;
        uint256 macroWindowTreshold;
        uint256 microWindowTreshold;
        uint256 targetValue;
    }

    string truflationRPC;
    JsonConfig config;
    AggregatorV3Interface feed;

    function setUp() public {
        truflationRPC = vm.envString("TRUFLATION_RPC");
        vm.createSelectFork(truflationRPC, 43_948_853);

        string memory root = vm.projectRoot();
        string memory path = append(root, "/config/truflationFeed.json");
        string memory json = vm.readFile(path);
        bytes memory jsonBytes = json.parseRaw("");

        config = abi.decode(jsonBytes, (JsonConfig));
        feed = AggregatorV3Interface(config.feedAddress);
    }

    function test() public {
        console2.log("Feed address: ", config.feedAddress);
        console2.log("Heartbeat: ", config.heartbeat);
        console2.log("Macro window treshold: ", config.macroWindowTreshold);
        console2.log("Micro window treshold: ", config.microWindowTreshold);
        console2.log("Target value: ", config.targetValue);
    }

    function testConsecutiveRoundId() public {
        (uint80 roundId,,,,) = feed.latestRoundData();
        console2.log("Latest round id: ", roundId);
        console2.log("Current block number: ", block.number);

        vm.createSelectFork(truflationRPC, block.number + (5 * 60 * 60));

        (uint80 nextRoundId,,,,) = feed.latestRoundData();
        console2.log("Next round id: ", nextRoundId);
        console2.log("Current block number: ", block.number);
    }
}
