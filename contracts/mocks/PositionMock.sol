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

    function initialOi(Position.Info memory pos) external view returns (uint256) {
        return pos.initialOi();
    }

    function oi(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares
    ) external view returns (uint256) {
        return pos.oi(totalOi, totalOiShares);
    }

    function value(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) external view returns (uint256) {
        return pos.value(totalOi, totalOiShares, currentPrice);
    }

    function isUnderwater(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) external view returns (bool) {
        return pos.isUnderwater(totalOi, totalOiShares, currentPrice);
    }

    function notional(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice
    ) external view returns (uint256) {
        return pos.notional(totalOi, totalOiShares, currentPrice);
    }

    function isLiquidatable(
        Position.Info memory pos,
        uint256 totalOi,
        uint256 totalOiShares,
        uint256 currentPrice,
        uint256 marginMaintenance
    ) external view returns (bool) {
        return pos.isLiquidatable(totalOi, totalOiShares, currentPrice, marginMaintenance);
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
