// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../../libraries/balancerv2/BalancerV2Tokens.sol";
import "../OverlayV1Feed.sol";
import "./IBalancerV2Vault.sol";

contract OverlayV1BalancerV2Feed is OverlayV1Feed {
    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private immutable VAULT;

    address public immutable marketPool;
    address public immutable ovlWethPool;
    address public immutable ovl;

    address public immutable marketToken0;
    address public immutable marketToken1;

    address public immutable ovlWethToken0;
    address public immutable ovlWethToken1;

    address public immutable marketBaseToken;
    address public immutable marketQuoteToken;
    uint128 public immutable marketBaseAmount;

    constructor(
        address _marketPool,
        address _ovlWethPool,
        address _ovl,
        address _marketBaseToken,
        address _marketQuoteToken,
        uint128 _marketBaseAmount,
        BalancerV2Tokens.Info memory balancerV2Tokens,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        VAULT = balancerV2Tokens.vault;
        // Check if gas cost is reduced by storing vault in memory
        IBalancerV2Vault vault = IBalancerV2Vault(balancerV2Tokens.vault);
        (IERC20[] memory marketTokens, , ) = getPoolTokensData(balancerV2Tokens.marketPoolId);

        // TODO: verify token ordering
        // need WETH in market pool to make reserve conversion from ETH => OVL
        address _marketToken0 = address(marketTokens[0]);
        address _marketToken1 = address(marketTokens[1]);

        require(_marketToken0 == WETH || _marketToken1 == WETH, "OVLV1Feed: marketToken != WETH");
        marketToken0 = _marketToken0;
        marketToken1 = _marketToken1;

        require(
            _marketToken0 == _marketBaseToken || _marketToken1 == _marketBaseToken,
            "OVLV1Feed: marketToken != marketBaseToken"
        );
        require(
            _marketToken0 == _marketQuoteToken || _marketToken1 == _marketQuoteToken,
            "OVLV1Feed: marketToken != marketQuoteToken"
        );
        marketBaseToken = _marketBaseToken;
        marketQuoteToken = _marketQuoteToken;
        marketBaseAmount = _marketBaseAmount;

        (IERC20[] memory ovlWethTokens, , ) = getPoolTokensData(balancerV2Tokens.ovlWethPoolId);

        // need OVL/WETH pool for ovl vs ETH price to make reserve conversion from ETH => OVL
        address _ovlWethToken0 = address(ovlWethTokens[0]);
        address _ovlWethToken1 = address(ovlWethTokens[1]);

        require(
            _ovlWethToken0 == WETH || _ovlWethToken1 == WETH,
            "OVLV1Feed: ovlWethToken != WETH"
        );
        require(
            _ovlWethToken0 == _ovl || _ovlWethToken1 == _ovl,
            "OVLV1Feed: ovlWethToken != OVL"
        );
        ovlWethToken0 = _ovlWethToken0;
        ovlWethToken1 = _ovlWethToken1;

        marketPool = _marketPool;
        ovlWethPool = _ovlWethPool;
        ovl = _ovl;
    }

    function getPoolTokensData(bytes32 balancerV2PoolId)
        public
        view
        returns (
            IERC20[] memory tokens,
            uint256[] memory balances,
            uint256 lastChangeBlock
        )
    {
        IBalancerV2Vault vault = IBalancerV2Vault(VAULT);
        (tokens, balances, lastChangeBlock) = vault.getPoolTokens(balancerV2PoolId);
        return (tokens, balances, lastChangeBlock);
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // TODO - put just enough code in to get this compiling
        // cache micro and macro windows for gas savings
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;

        // consult to market pool
        // secondsAgo.length = 4; twaps.length = liqs.length = 3
        (
            uint32[] memory secondsAgos,
            uint32[] memory windows,
            uint256[] memory nowIdxs
        ) = _inputsToConsultMarketPool(_microWindow, _macroWindow);

        uint256[] memory prices = new uint256[](nowIdxs.length);
        uint256 price = 10;
        prices[0] = 10;
        uint256 reserve = 10;

        return
            Oracle.Data({
                timestamp: block.timestamp,
                microWindow: _microWindow,
                macroWindow: _macroWindow,
                priceOverMicroWindow: prices[2], // secondsAgos = _microWindow
                priceOverMacroWindow: prices[1], // secondsAgos = _macroWindow
                priceOneMacroWindowAgo: prices[0], // secondsAgos = _macroWindow * 2
                reserveOverMicroWindow: reserve,
                hasReserve: true
            });
    }

    /// @dev returns input params needed for call to marketPool consult
    function _inputsToConsultMarketPool(uint256 _microWindow, uint256 _macroWindow)
        private
        pure
        returns (
            uint32[] memory,
            uint32[] memory,
            uint256[] memory
        )
    {
        uint32[] memory secondsAgos = new uint32[](4);
        uint32[] memory windows = new uint32[](3);
        uint256[] memory nowIdxs = new uint256[](3);

        // number of seconds in past for which we want accumulator snapshot
        // for Oracle.Data, need:
        //  1. now (0 s ago)
        //  2. now - microWindow (microWindow seconds ago)
        //  3. now - macroWindow (macroWindow seconds ago)
        //  4. now - 2 * macroWindow (2 * macroWindow seconds ago)
        secondsAgos[0] = uint32(_macroWindow * 2);
        secondsAgos[1] = uint32(_macroWindow);
        secondsAgos[2] = uint32(_microWindow);
        secondsAgos[3] = 0;

        // window lengths for each cumulative differencing
        // in terms of prices, will use for indexes
        //  0: priceOneMacroWindowAgo
        //  1: priceOverMacroWindow
        //  2: priceOverMicroWindow
        windows[0] = uint32(_macroWindow);
        windows[1] = uint32(_macroWindow);
        windows[2] = uint32(_microWindow);

        // index in secondsAgos which we treat as current time when differencing
        // for mean calcs
        nowIdxs[0] = 1;
        nowIdxs[1] = secondsAgos.length - 1;
        nowIdxs[2] = secondsAgos.length - 1;

        return (secondsAgos, windows, nowIdxs);
    }
}
