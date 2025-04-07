// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "../OverlayV1Feed.sol";
import "../../interfaces/IOverlayV1Token.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

contract OverlayV1ChainlinkFeedZero is OverlayV1Feed {
    IOverlayV1Token public immutable ovl;
    AggregatorV3Interface public immutable aggregator;
    uint8 public immutable decimals;
    uint256 public heartbeat;
    string public description;

    event HeartbeatSet(uint256 heartbeat);

    modifier onlyGovernor() {
        require(ovl.hasRole(GOVERNOR_ROLE, msg.sender), "OVLV1: !governor");
        _;
    }

    constructor(
        address _ovl,
        address _aggregator,
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _heartbeat
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        require(_aggregator != address(0), "Invalid feed");

        aggregator = AggregatorV3Interface(_aggregator);
        decimals = aggregator.decimals();
        description = aggregator.description();
        _setHeartbeat(_heartbeat);
        ovl = IOverlayV1Token(_ovl);
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        (uint80 roundId, int256 spotPrice,, uint256 updatedAt,) = aggregator.latestRoundData();

        if (updatedAt < block.timestamp - heartbeat) revert("stale price feed");

        (
            uint256 priceOverMicroWindow,
            uint256 priceOverMacroWindow,
            uint256 priceOneMacroWindowAgo
        ) = _getAveragePrice(roundId, spotPrice);

        return Oracle.Data({
            timestamp: block.timestamp,
            microWindow: microWindow,
            macroWindow: macroWindow,
            priceOverMicroWindow: priceOverMicroWindow,
            priceOverMacroWindow: priceOverMacroWindow,
            priceOneMacroWindowAgo: priceOneMacroWindowAgo,
            reserveOverMicroWindow: 0,
            hasReserve: false
        });
    }

    function _getAveragePrice(uint80 roundId, int256 spotPrice)
        internal
        view
        returns (
            uint256 priceOverMicroWindow,
            uint256 priceOverMacroWindow,
            uint256 priceOneMacroWindowAgo
        )
    {
        // nextTimestamp will be next time stamp recorded from current round id
        uint256 nextTimestamp = block.timestamp;
        // these values will keep decreasing till zero, until all data is used up in respective window
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;

        // timestamp till which value need to be considered for macrowindow ago
        uint256 macroAgoTargetTimestamp = nextTimestamp - 2 * macroWindow;

        uint256 sumOfPriceMicroWindow;
        uint256 sumOfPriceMacroWindow;
        uint256 sumOfPriceMacroWindowAgo;

        while (true) {
            (, int256 answer,, uint256 updatedAt,) = aggregator.getRoundData(roundId);

            if (_microWindow > 0) {
                uint256 dt = nextTimestamp - updatedAt < _microWindow
                    ? nextTimestamp - updatedAt
                    : _microWindow;
                sumOfPriceMicroWindow += dt * uint256(answer);
                _microWindow -= dt;
            }

            if (_macroWindow > 0) {
                uint256 dt = nextTimestamp - updatedAt < _macroWindow
                    ? nextTimestamp - updatedAt
                    : _macroWindow;
                sumOfPriceMacroWindow += dt * uint256(answer);
                _macroWindow -= dt;
            }

            if (updatedAt <= block.timestamp - macroWindow) {
                uint256 startTime = nextTimestamp > block.timestamp - macroWindow
                    ? block.timestamp - macroWindow
                    : nextTimestamp;
                if (updatedAt >= macroAgoTargetTimestamp) {
                    sumOfPriceMacroWindowAgo += (startTime - updatedAt) * uint256(answer);
                } else {
                    sumOfPriceMacroWindowAgo +=
                        (startTime - macroAgoTargetTimestamp) * uint256(answer);
                    break;
                }
            }

            nextTimestamp = updatedAt;
            roundId--;
        }

        priceOverMicroWindow =
            (sumOfPriceMicroWindow * (10 ** 18)) / (microWindow * 10 ** aggregator.decimals());
        priceOverMacroWindow =
            (sumOfPriceMacroWindow * (10 ** 18)) / (macroWindow * 10 ** aggregator.decimals());
        priceOneMacroWindowAgo =
            (sumOfPriceMacroWindowAgo * (10 ** 18)) / (macroWindow * 10 ** aggregator.decimals());

        uint256 scaledSpotPrice = uint256(spotPrice) * 10 ** (18 - uint256(aggregator.decimals()));
        priceOverMicroWindow = priceOverMacroWindow > priceOverMicroWindow
            ? Math.min(scaledSpotPrice, priceOverMicroWindow)
            : Math.max(scaledSpotPrice, priceOverMicroWindow);
    }

    function setHeartbeat(uint256 _heartbeat) external onlyGovernor {
        _setHeartbeat(_heartbeat);
    }

    function _setHeartbeat(uint256 _heartbeat) internal {
        heartbeat = _heartbeat;
        emit HeartbeatSet(_heartbeat);
    }
}
