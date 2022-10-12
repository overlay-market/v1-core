// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "../OverlayV1Feed.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract OverlayV1ChainlinkFeed is OverlayV1Feed {
    uint128 internal constant ONE = 1e18; // 18 decimal places for ovl

    AggregatorV3Interface public immutable aggregator;

    constructor(
        address _aggregator,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        require(_aggregator != address(0), "Invalid feed");

        aggregator = AggregatorV3Interface(_aggregator);
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {

        (uint80 roundId,,,,) = aggregator.latestRoundData();

        return
            Oracle.Data({
                timestamp: block.timestamp,
                microWindow: microWindow,
                macroWindow: macroWindow,
                priceOverMicroWindow: _getAveragePrice(microWindow, roundId, false),
                priceOverMacroWindow: _getAveragePrice(macroWindow, roundId, false),
                priceOneMacroWindowAgo: _getAveragePrice(macroWindow, roundId, true),
                reserveOverMicroWindow: 0,
                hasReserve: false
            });
    }

    function _getAveragePrice(
        uint256 windowLength,
        uint80 roundId,
        bool windowAgo
    ) internal view returns (uint256) {
        uint256 nextTimestamp = windowAgo ? block.timestamp - windowLength : block.timestamp;
        uint256 targetTimestamp = nextTimestamp - windowLength;
        uint256 sumOfPrice;

        while (true) {
            (, int256 answer, , uint256 updatedAt, ) = aggregator.getRoundData(roundId);

            if (windowAgo) {
                if (updatedAt > nextTimestamp) {
                    roundId--;
                    continue;
                }
            }

            if (updatedAt >= targetTimestamp) {
                sumOfPrice += (nextTimestamp - updatedAt) * uint256(answer);
            } else {
                sumOfPrice += (nextTimestamp - targetTimestamp) * uint256(answer);
                break;
            }

            nextTimestamp = updatedAt;
            roundId--;
        }

        return ((sumOfPrice / windowLength) * 10**18) / 10**aggregator.decimals();
    }
}
