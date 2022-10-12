// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Aggregator is AggregatorV3Interface {
    
    struct RoundData {
        int256 answer;
        uint256 startedAt;
        uint256 updatedAt;
        uint80 answeredInRound;
    }

    mapping(uint80 => RoundData) internal roundData;

    uint80 public latestRoundId;

    function version() public view override returns (uint256) {
        return 1;
    }

    function description() public view override returns (string memory) {
        return "Mock Desc";
    }

    function decimals() public view override returns (uint8) {
        return 8;
    }

    function setData(uint80 _roundId, int256 answer) external {
        roundData[_roundId] = RoundData({
            answer: answer,
            startedAt: block.timestamp,
            updatedAt: block.timestamp,
            answeredInRound: _roundId
        });
        latestRoundId = _roundId;
    }

    function latestRoundData()
        public
        view
        override
        returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        )
    {
        RoundData memory round = roundData[latestRoundId];
        return (
            latestRoundId,
            round.answer,
            round.startedAt,
            round.updatedAt,
            round.answeredInRound
        );
    }

    function getRoundData(uint80 _roundId)
        public
        view
        override
        returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        )
    {
        RoundData memory round = roundData[_roundId];
        return (_roundId, round.answer, round.startedAt, round.updatedAt, round.answeredInRound);
    }
}
