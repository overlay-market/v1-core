// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract TradingMining is Ownable {

    uint64 public immutable startTime;
    uint64 public immutable epochDuration;

    uint256 public immutable epochReward;

    IERC20 public immutable rewardToken1;
    IERC20 public rewardToken2;

    uint8 public token1Percentage;

    uint256 public immutable maxRewardPerEpochPerAddress;

    mapping(address trader => mapping(uint256 epoch => bool claimed)) public claims;

    error InvalidPercentage();
    error InvalidRewardToken2();

    constructor(
        uint64 _startTime,
        uint64 _epochDuration,
        uint256 _epochReward,
        address _rewardToken1,
        address _rewardToken2,
        uint8 _token1Percentage,
        uint256 _maxRewardPerEpochPerAddress
    ) {
        startTime = _startTime;
        epochDuration = _epochDuration;
        epochReward = _epochReward;
        rewardToken1 = IERC20(_rewardToken1);
        setRewardToken2(_rewardToken2, _token1Percentage); 
        maxRewardPerEpochPerAddress = _maxRewardPerEpochPerAddress;
    }

    function setRewardToken2(address _rewardToken2, uint8 _token1Percentage) public onlyOwner {
        if (_token1Percentage > 100) revert InvalidPercentage();
        if (_rewardToken2 == address(0) && _token1Percentage < 100) revert InvalidRewardToken2();
        rewardToken2 = IERC20(_rewardToken2);
        token1Percentage = _token1Percentage;
    }

    function getCurrentEpoch() public view returns (uint256) {
        return (block.timestamp - startTime) / epochDuration;
    }

    function claimed(address trader, uint256 epoch) public view returns (bool) {
        return claims[trader][epoch];
    }

}
