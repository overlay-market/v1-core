// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "../OverlayV1Feed.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract OverlayV1ChainlinkFeed is OverlayV1Feed {

    uint128 internal constant ONE = 1e18; // 18 decimal places for ovl

    AggregatorV3Interface immutable public aggregator;

    constructor(
        address _aggregator,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1Feed(_microWindow, _macroWindow) {

        require(_aggregator != address(0), "Invalid feed");

        aggregator = AggregatorV3Interface(_aggregator);
    
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {

        (uint80 roundId, int256 answer,,,) = aggregator.latestRoundData();
        uint256 decimalNormalized = (uint256(answer) * 10**18)/10**aggregator.decimals();

        return Oracle.Data({
            timestamp: block.timestamp,
            microWindow: microWindow,
            macroWindow: macroWindow,
            priceOverMicroWindow: _getAveragePriceOverWindow(macroWindow, roundId),
            priceOverMacroWindow: _getAveragePriceOverWindow(microWindow, roundId),
            priceOneMacroWindowAgo: _getAveragePriceWindowAgo(macroWindow, roundId),
            reserveOverMicroWindow: uint256(decimalNormalized),
            hasReserve: false            
        });
    }


    function _getAveragePriceOverWindow(uint256 windowLength,uint80 roundId) internal view returns (uint256) {
        uint256 sumOfPrice;
        uint256 nextTimestamp = block.timestamp;
        uint256 targetTimestamp = nextTimestamp - windowLength;
        while(true){

            (,int256 answer,,uint256 updatedAt,) = aggregator.getRoundData(roundId);
            if(updatedAt >= targetTimestamp) {
                sumOfPrice += (nextTimestamp - updatedAt)*uint256(answer); 
            }else{
                sumOfPrice += (nextTimestamp - targetTimestamp)*uint256(answer);
                break;
            }

            nextTimestamp = updatedAt;
            roundId--;
        }

        return ((sumOfPrice/windowLength) * 10**18)/10**aggregator.decimals();
    }


    function _getAveragePriceWindowAgo(uint256 windowLength, uint80 roundId) internal view returns (uint256) {

        uint256 nextTimestamp = block.timestamp - windowLength;
        uint256 targetTimestamp = nextTimestamp - windowLength;
        uint256 sumOfPrice;

        while(true) {
            (,int256 answer,,uint256 updatedAt,) = aggregator.getRoundData(roundId);
            if(updatedAt > nextTimestamp) {
                roundId--;
                continue;
            }
            if(updatedAt >= targetTimestamp) {
                sumOfPrice += (nextTimestamp - updatedAt)*uint256(answer); 
            }else{
                sumOfPrice += (nextTimestamp - targetTimestamp)*uint256(answer);
                break;
            }

            nextTimestamp = updatedAt;
            roundId--;            
        }


        return ((sumOfPrice/windowLength) * 10**18)/10**aggregator.decimals();

    }
    
}