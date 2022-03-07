// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2Pool.sol";
import "../../libraries/balancerv2/BalancerV2Tokens.sol";
import "../../libraries/balancerv2/BalancerV2PoolInfo.sol";
import "../OverlayV1Feed.sol";
import "./IBalancerV2Vault.sol";
import "./IBalancerV2PriceOracle.sol";

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
        BalancerV2PoolInfo.Pool memory balancerV2Pool,
        BalancerV2Tokens.Info memory balancerV2Tokens,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        VAULT = balancerV2Tokens.vault;
        // Check if gas cost is reduced by storing vault in memory
        IBalancerV2Vault vault = IBalancerV2Vault(balancerV2Tokens.vault);
        (IERC20[] memory marketTokens, , ) = getPoolTokensData(balancerV2Tokens.marketPoolId);

        require(
            getPoolId(balancerV2Pool.marketPool) == balancerV2Tokens.marketPoolId,
            "OVLV1Feed: marketPoolId mismatch"
        );

        require(
            getPoolId(balancerV2Pool.ovlWethPool) == balancerV2Tokens.ovlWethPoolId,
            "OVLV1Feed: ovlWethPoolId mismatch"
        );

        // TODO: verify token ordering
        // need WETH in market pool to make reserve conversion from ETH => OVL
        address _marketToken0 = address(marketTokens[0]);
        address _marketToken1 = address(marketTokens[1]);

        require(_marketToken0 == WETH || _marketToken1 == WETH, "OVLV1Feed: marketToken != WETH");
        marketToken0 = _marketToken0;
        marketToken1 = _marketToken1;

        require(
            _marketToken0 == balancerV2Pool.marketBaseToken ||
                _marketToken1 == balancerV2Pool.marketBaseToken,
            "OVLV1Feed: marketToken != marketBaseToken"
        );
        require(
            _marketToken0 == balancerV2Pool.marketQuoteToken ||
                _marketToken1 == balancerV2Pool.marketQuoteToken,
            "OVLV1Feed: marketToken != marketQuoteToken"
        );

        marketBaseToken = balancerV2Pool.marketBaseToken;
        marketQuoteToken = balancerV2Pool.marketQuoteToken;
        marketBaseAmount = balancerV2Pool.marketBaseAmount;

        (IERC20[] memory ovlWethTokens, , ) = getPoolTokensData(balancerV2Tokens.ovlWethPoolId);

        // need OVL/WETH pool for ovl vs ETH price to make reserve conversion from ETH => OVL
        address _ovlWethToken0 = address(ovlWethTokens[0]);
        address _ovlWethToken1 = address(ovlWethTokens[1]);

        require(
            _ovlWethToken0 == WETH || _ovlWethToken1 == WETH,
            "OVLV1Feed: ovlWethToken != WETH"
        );
        require(
            _ovlWethToken0 == balancerV2Pool.ovl || _ovlWethToken1 == balancerV2Pool.ovl,
            "OVLV1Feed: ovlWethToken != OVL"
        );
        ovlWethToken0 = _ovlWethToken0;
        ovlWethToken1 = _ovlWethToken1;

        marketPool = balancerV2Pool.marketPool;
        ovlWethPool = balancerV2Pool.ovlWethPool;
        ovl = balancerV2Pool.ovl;
    }

    /// @notice Returns the time average weighted price corresponding to each of `queries`.
    /// @dev Prices are dev represented as 18 decimal fixed point values.
    /// @dev PAIR_PRICE: the price of the tokens in the Pool, expressed as the price of the second
    /// @dev token in units of the first token. For example, if token A is worth $2, and token B is
    /// @dev worth $4, the pair price will be 2.0. Note that the price is computed *including* the
    /// @dev tokens decimals. This means that the pair price of a Pool with DAI and USDC will be
    /// @dev close to 1.0, despite DAI having 18 decimals and USDC 6.
    function getTimeWeightedAverage(
      uint256 secs,
      uint256 ago
    ) public view returns (
    uint256[] memory results
    ) {
      address poolWethDai = 0x0b09deA16768f0799065C475bE02919503cB2a35;
      IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(poolWethDai);
      IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.PAIR_PRICE;
      uint256 secs = 1800;
      uint256 ago = 0;

      // IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
      // IBalancerV2PriceOracle.OracleAverageQuery[1] memory queries;
      // queries[0] = query;
      // uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);

      IBalancerV2PriceOracle.OracleAverageQuery[] memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
      IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
      queries[0] = query;
      uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);

      uint256 latest = priceOracle.getLatest(variable);
      return results;
    }
    /// @notice Returns the time average weighted price corresponding to each of `queries`.
    /// @dev Prices are dev represented as 18 decimal fixed point values.
    /// @dev PAIR_PRICE: the price of the tokens in the Pool, expressed as the price of the second
    /// @dev token in units of the first token. For example, if token A is worth $2, and token B is
    /// @dev worth $4, the pair price will be 2.0. Note that the price is computed *including* the
    /// @dev tokens decimals. This means that the pair price of a Pool with DAI and USDC will be
    /// @dev close to 1.0, despite DAI having 18 decimals and USDC 6.
    function getTimeWeightedAveragePairPrice(uint256 secs, uint256 ago) public view returns (uint256[] memory results) {
      address poolWethDai = 0x0b09deA16768f0799065C475bE02919503cB2a35;
      IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(poolWethDai);
      IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.PAIR_PRICE;
      uint256 secs = 1800;
      uint256 ago = 0;

      // IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
      // IBalancerV2PriceOracle.OracleAverageQuery[1] memory queries;
      // queries[0] = query;
      // uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);

      IBalancerV2PriceOracle.OracleAverageQuery[] memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
      IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
      queries[0] = query;
      uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);

      uint256 latest = priceOracle.getLatest(variable);
      return results;
    }

    /// @notice Returns the time average weighted price corresponding to each of `queries`.
    /// @dev INVARIANT: the value of the Pool's invariant, which serves as a measure of its
    /// @dev liquidity.
    function getTimeWeightedAverageInvariant(
      uint256 secs,
      uint256 ago
    ) public view returns (
    uint256[] memory results
    ) {
      address poolWethDai = 0x0b09deA16768f0799065C475bE02919503cB2a35;
      IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(poolWethDai);
      IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.INVARIANT;

      // IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
      // IBalancerV2PriceOracle.OracleAverageQuery[1] memory queries;
      // queries[0] = query;
      // uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);

      IBalancerV2PriceOracle.OracleAverageQuery[] memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
      IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
      queries[0] = query;
      uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);

      uint256 latest = priceOracle.getLatest(variable);
      return results;
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

    function getPoolId(address pool) public view returns (bytes32) {
        return IBalancerV2Pool(pool).getPoolId();
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

    /// @dev returns input params needed for call to ovlWethPool consult
    function _inputsToConsultOvlWethPool(uint256 _microWindow, uint256 _macroWindow)
        private
        pure
        returns (
            uint32[] memory,
            uint32[] memory,
            uint256[] memory
        )
    {
        uint32[] memory secondsAgos = new uint32[](2);
        uint32[] memory windows = new uint32[](1);
        uint256[] memory nowIdxs = new uint256[](1);

        // number of seconds in past for which we want accumulator snapshot
        // for Oracle.Data, need:
        //  1. now (0 s ago)
        //  2. now - microWindow (microWindow seconds ago)
        secondsAgos[0] = uint32(_microWindow);
        secondsAgos[1] = 0;

        // window lengths for each cumulative differencing
        // in terms of prices, will use for indexes
        //  0: priceOvlWethOverMicroWindow
        windows[0] = uint32(_microWindow);

        // index in secondsAgos which we treat as current time when differencing
        // for mean calcs
        nowIdxs[0] = secondsAgos.length - 1;

        return (secondsAgos, windows, nowIdxs);
    }
}
