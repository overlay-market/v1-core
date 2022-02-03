// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "../libraries/Position.sol";

contract PositionMock {
    using Position for mapping(bytes32 => Position.Info);
    using Position for Position.Info;

    mapping(bytes32 => Position.Info) public positions;

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

    function exists(Position.Info memory pos) external view returns (bool) {
        return pos.exists();
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
