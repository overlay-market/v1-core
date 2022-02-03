// SPDX-License-Identifier: MIT
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
                    POSITION GETTER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function exists(Position.Info memory pos) external view returns (bool) {
        return pos.exists();
    }

    /*///////////////////////////////////////////////////////////////
                        POSITION CALC FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function oiSharesCurrent(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return pos.oiSharesCurrent(fraction);
    }

    function debtCurrent(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return pos.debtCurrent(fraction);
    }

    function oiInitial(Position.Info memory pos, uint256 fraction)
        external
        view
        returns (uint256)
    {
        return pos.oiInitial(fraction);
    }

    function cost(Position.Info memory pos, uint256 fraction) external view returns (uint256) {
        return pos.cost(fraction);
    }

    function oiCurrent(
        Position.Info memory pos,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares
    ) external view returns (uint256) {
        return pos.oiCurrent(fraction, totalOi, totalOiShares);
    }

    function value(
        Position.Info memory pos,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff
    ) external view returns (uint256) {
        return pos.value(fraction, totalOi, totalOiShares, currentPrice, capPayoff);
    }

    function notional(
        Position.Info memory pos,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff
    ) external view returns (uint256) {
        return pos.notional(fraction, totalOi, totalOiShares, currentPrice, capPayoff);
    }

    function tradingFee(
        Position.Info memory pos,
        uint256 fraction,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 tradingFeeRate
    ) external view returns (uint256) {
        return
            pos.tradingFee(
                fraction,
                totalOi,
                totalOiShares,
                currentPrice,
                capPayoff,
                tradingFeeRate
            );
    }

    function isLiquidatable(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 capPayoff,
        uint256 marginMaintenance
    ) external view returns (bool) {
        return
            pos.isLiquidatable(totalOi, totalOiShares, currentPrice, capPayoff, marginMaintenance);
    }

    function liquidationPrice(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 marginMaintenance
    ) external view returns (uint256) {
        return pos.liquidationPrice(totalOi, totalOiShares, marginMaintenance);
    }
}
