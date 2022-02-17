// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "../../libraries/balancerv2/BalancerV2Tokens.sol";
import "../../libraries/balancerv2/BalancerV2PoolInfo.sol";
import "../OverlayV1FeedFactory.sol";
import "./OverlayV1BalancerV2Feed.sol";

contract OverlayV1BalancerV2Factory is OverlayV1FeedFactory {
    using BalancerV2Tokens for BalancerV2Tokens.Info;
    using BalancerV2PoolInfo for BalancerV2PoolInfo.Pool;
    address public immutable ovlWethPool;
    address public immutable ovl;

    // registry of feeds; for a given (pool, base, quote, amount) pair, returns associated feed
    mapping(address => mapping(address => mapping(address => mapping(uint128 => address))))
        public getFeed;

    /// @notice Constructs a new OverlayV1UniswapV3Factory contract for used to deploy new
    /// @notice UniswapV3 feeds to be offered as a market
    /// @param _ovlWethPool Address of OVL <-> WETH pool being offered as a market
    /// @param _ovl Address of OVL tokens
    /// @param _microWindow Micro window to define TWAP over (typically 600s)
    /// @param _macroWindow Macro window to define TWAP over (typically 3600s)
    constructor(
        address _ovlWethPool,
        address _ovl,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1FeedFactory(_microWindow, _macroWindow) {
        ovlWethPool = _ovlWethPool;
        ovl = _ovl;
    }

    /// @notice Deploys a new OverlayV1BalancerV2Feed contract
    /// @param marketPool Address of pool being offered as a market
    /// @param marketBaseToken The base token address of the pool
    /// @param marketQuoteToken The quote token address of the pool
    /// @param marketBaseAmount TODO
    function deployFeed(
        address marketPool,
        address marketBaseToken,
        address marketQuoteToken,
        uint128 marketBaseAmount,
        BalancerV2Tokens.Info memory balancerV2Tokens
    ) external returns (address feed_) {
        require(
            getFeed[marketPool][marketBaseToken][marketQuoteToken][marketBaseAmount] == address(0),
            "OVLV1: feed already exists"
        );

        BalancerV2PoolInfo.Pool memory balancerV2Pool = BalancerV2PoolInfo.Pool(
          marketPool,
          ovlWethPool,
          ovl,
          marketBaseToken,
          marketQuoteToken,
          marketBaseAmount
        );

        // Use the CREATE2 opcode to deploy a new Feed contract.
        // Will revert if feed which accepts (marketPool, marketBaseToken, marketQuoteToken,
        // marketBaseAmount) in its constructor has already been deployed since salt would be the
        // same and can't deploy with it twice.
        feed_ = address(
            new OverlayV1BalancerV2Feed{
                salt: keccak256(
                    abi.encode(marketPool, marketBaseToken, marketQuoteToken, marketBaseAmount)
                )
            }(
                balancerV2Pool,
                balancerV2Tokens,
                microWindow,
                macroWindow
            )
        );

        // store feed registry record for (marketPool, marketBaseToken, marketQuoteToken) combo
        // and record address as deployed feed
        getFeed[marketPool][marketBaseToken][marketQuoteToken][marketBaseAmount] = feed_;
        isFeed[feed_] = true;
        emit FeedDeployed(msg.sender, feed_);
    }
}
