// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "../OverlayV1Feed.sol";
import "../../interfaces/IOverlayV1Token.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

contract OverlayV1ChainlinkFeedRatio is OverlayV1Feed {
    IOverlayV1Token public immutable ovl;
    AggregatorV3Interface public immutable baseAggregator;
    AggregatorV3Interface public immutable quoteAggregator;
    uint8 public immutable baseDecimals;
    uint8 public immutable quoteDecimals;
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
        address _baseAggregator,
        address _quoteAggregator,
        uint256 _microWindow,
        uint256 _macroWindow,
        uint256 _heartbeat
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        require(_baseAggregator != address(0), "OVLV1: !base");
        require(_quoteAggregator != address(0), "OVLV1: !quote");

        baseAggregator = AggregatorV3Interface(_baseAggregator);
        quoteAggregator = AggregatorV3Interface(_quoteAggregator);

        baseDecimals = baseAggregator.decimals();
        quoteDecimals = quoteAggregator.decimals();

        require(baseDecimals <= 18, "OVLV1: base decimals > 18");
        require(quoteDecimals <= 18, "OVLV1: quote decimals > 18");

        decimals = 18;

        description = string(
            abi.encodePacked(
                baseAggregator.description(),
                " / ",
                quoteAggregator.description()
            )
        );

        _setHeartbeat(_heartbeat);
        ovl = IOverlayV1Token(_ovl);
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        uint256 priceOverMicroWindow;
        uint256 priceOverMacroWindow;
        uint256 priceOneMacroWindowAgo;
        uint256 scaledSpotRatio;

        {
            (uint80 baseRoundId, int256 baseSpot,, uint256 baseUpdatedAt,) =
                baseAggregator.latestRoundData();
            (uint80 quoteRoundId, int256 quoteSpot,, uint256 quoteUpdatedAt,) =
                quoteAggregator.latestRoundData();

            if (baseUpdatedAt < block.timestamp - heartbeat) revert("OVLV1: !base stale");
            if (quoteUpdatedAt < block.timestamp - heartbeat) revert("OVLV1: !quote stale");

            require(baseSpot > 0, "OVLV1: !base spot");
            require(quoteSpot > 0, "OVLV1: !quote spot");

            (
                uint256 baseMicro,
                uint256 baseMacro,
                uint256 baseMacroAgo
            ) = _getAveragePrice(baseAggregator, baseRoundId, baseDecimals);

            (
                uint256 quoteMicro,
                uint256 quoteMacro,
                uint256 quoteMacroAgo
            ) = _getAveragePrice(quoteAggregator, quoteRoundId, quoteDecimals);

            require(quoteMicro > 0, "OVLV1: !quote micro");
            require(quoteMacro > 0, "OVLV1: !quote macro");
            require(quoteMacroAgo > 0, "OVLV1: !quote macroAgo");

            require(baseMicro > 0, "OVLV1: !base micro");
            require(baseMacro > 0, "OVLV1: !base macro");
            require(baseMacroAgo > 0, "OVLV1: !base macroAgo");

            priceOverMicroWindow = (baseMicro * 1e18) / quoteMicro;
            priceOverMacroWindow = (baseMacro * 1e18) / quoteMacro;
            priceOneMacroWindowAgo = (baseMacroAgo * 1e18) / quoteMacroAgo;

            uint256 scaledBaseSpot = uint256(baseSpot) * 10 ** (18 - baseDecimals);
            uint256 scaledQuoteSpot = uint256(quoteSpot) * 10 ** (18 - quoteDecimals);
            scaledSpotRatio = (scaledBaseSpot * 1e18) / scaledQuoteSpot;
        }

        if (priceOverMacroWindow > priceOverMicroWindow) {
            priceOverMicroWindow = Math.min(scaledSpotRatio, priceOverMicroWindow);
            priceOverMacroWindow = Math.max(scaledSpotRatio, priceOverMacroWindow);
        } else if (priceOverMacroWindow < priceOverMicroWindow) {
            priceOverMicroWindow = Math.max(scaledSpotRatio, priceOverMicroWindow);
            priceOverMacroWindow = Math.min(scaledSpotRatio, priceOverMacroWindow);
        } else {
            priceOverMicroWindow = scaledSpotRatio;
        }

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


    function _getAveragePrice(
        AggregatorV3Interface aggregator,
        uint80 roundId,
        uint8 aggregatorDecimals
    )
        internal
        view
        returns (
            uint256 priceOverMicroWindow,
            uint256 priceOverMacroWindow,
            uint256 priceOneMacroWindowAgo
        )
    {
        uint256 nextTimestamp = block.timestamp;
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;
        uint256 macroAgoTargetTimestamp = nextTimestamp - 2 * macroWindow;

        uint256 sumOfPriceMicroWindow;
        uint256 sumOfPriceMacroWindow;
        uint256 sumOfPriceMacroWindowAgo;

        while (true) {
            {
                (, int256 answer,, uint256 updatedAt,) = aggregator.getRoundData(roundId);

                require(answer > 0, "OVLV1: !answer");
                require(updatedAt > 0, "OVLV1: !updatedAt");

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
            }
            if (roundId == 0) break;
            unchecked { roundId--; }
        }

        uint256 aggDecScale = 10 ** aggregatorDecimals;
        priceOverMicroWindow = (sumOfPriceMicroWindow * 1e18) / (microWindow * aggDecScale);
        priceOverMacroWindow = (sumOfPriceMacroWindow * 1e18) / (macroWindow * aggDecScale);
        priceOneMacroWindowAgo = (sumOfPriceMacroWindowAgo * 1e18) / (macroWindow * aggDecScale);
    }


    function setHeartbeat(uint256 _heartbeat) external onlyGovernor {
        _setHeartbeat(_heartbeat);
    }

    function _setHeartbeat(uint256 _heartbeat) internal {
        heartbeat = _heartbeat;
        emit HeartbeatSet(_heartbeat);
    }

}
