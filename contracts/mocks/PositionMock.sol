// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../libraries/Position.sol";

contract PositionMock {
    using Position for mapping(bytes32 => Position.Info);
    using Position for Position.Info;

    mapping(bytes32 => Position.Info) public positions;

    /*///////////////////////////////////////////////////////////////
                        POSITIONS MAPPING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function get(address owner, uint256 id) external view returns (Position.Info memory) {
        Position.Info memory position = positions.get(owner, id);
        return position;
    }

    function set(
        address owner,
        uint256 id,
        Position.Info memory pos
    ) external {
        positions.set(owner, id, pos);
    }

    /*///////////////////////////////////////////////////////////////
                     POSITION EXISTENCE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function exists(Position.Info memory pos) external view returns (bool) {
        return pos.exists();
    }

    /*///////////////////////////////////////////////////////////////
                 POSITION FRACTION REMAINING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function getFractionRemaining(Position.Info memory pos) external view returns (uint256) {
        return pos.getFractionRemaining();
    }

    function updatedFractionRemaining(Position.Info memory pos, uint256 fractionRemoved)
        external
        view
        returns (uint16)
    {
        return pos.updatedFractionRemaining(fractionRemoved);
    }

    /*///////////////////////////////////////////////////////////////
                    POSITION PRICE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function midPriceAtEntry(Position.Info memory pos) external view returns (uint256) {
        return pos.midPriceAtEntry();
    }

    function entryPrice(Position.Info memory pos) external view returns (uint256) {
        return pos.entryPrice();
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION OI FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function calcOiShares(
        uint256 oi,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide
    ) external view returns (uint256) {
        return Position.calcOiShares(oi, oiTotalOnSide, oiTotalSharesOnSide);
    }

    /*///////////////////////////////////////////////////////////////
                  POSITION FRACTIONAL GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function notionalInitial(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return Position.notionalInitial(pos, fraction);
    }

    function oiInitial(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return pos.oiInitial(fraction);
    }

    function oiSharesCurrent(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return pos.oiSharesCurrent(fraction);
    }

    function debtInitial(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return Position.debtInitial(pos, fraction);
    }

    function oiCurrent(
        Position.Info memory pos,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide
    ) external view returns (uint256) {
        return pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide);
    }

    function cost(Position.Info memory pos, uint256 fraction) external view returns (uint256) {
        return pos.cost(fraction);
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function value(
        Position.Info memory pos,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff
    ) external view returns (uint256) {
        return pos.value(fraction, oiTotalOnSide, oiTotalSharesOnSide, currentPrice, capPayoff);
    }

    function notionalWithPnl(
        Position.Info memory pos,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff
    ) external view returns (uint256) {
        return
            pos.notionalWithPnl(
                fraction,
                oiTotalOnSide,
                oiTotalSharesOnSide,
                currentPrice,
                capPayoff
            );
    }

    function tradingFee(
        Position.Info memory pos,
        uint256 fraction,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 tradingFeeRate
    ) external view returns (uint256) {
        return
            pos.tradingFee(
                fraction,
                oiTotalOnSide,
                oiTotalSharesOnSide,
                currentPrice,
                capPayoff,
                tradingFeeRate
            );
    }

    function liquidatable(
        Position.Info memory pos,
        uint256 oiTotalOnSide,
        uint256 oiTotalSharesOnSide,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 maintenanceMarginFraction,
        uint256 liquidationFeeRate
    ) external view returns (bool) {
        return
            pos.liquidatable(
                oiTotalOnSide,
                oiTotalSharesOnSide,
                currentPrice,
                capPayoff,
                maintenanceMarginFraction,
                liquidationFeeRate
            );
    }
}
