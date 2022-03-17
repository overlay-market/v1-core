// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../OverlayV1Feed.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2Pool.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2Vault.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2PriceOracle.sol";
import "../../libraries/balancerv2/BalancerV2Tokens.sol";
import "../../libraries/balancerv2/BalancerV2PoolInfo.sol";

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

    bytes32 public immutable ovlWethPoolId;

    constructor(
        BalancerV2PoolInfo.Pool memory balancerV2Pool,
        BalancerV2Tokens.Info memory balancerV2Tokens,
        uint256 _microWindow,
        uint256 _macroWindow
    ) OverlayV1Feed(_microWindow, _macroWindow) {
        ovlWethPoolId = balancerV2Tokens.ovlWethPoolId;
        VAULT = balancerV2Tokens.vault;
        // Check if gas cost is reduced by storing vault in memory
        IBalancerV2Vault vault = IBalancerV2Vault(balancerV2Tokens.vault);
        (IERC20[] memory marketTokens, , ) = getPoolTokens(balancerV2Tokens.marketPoolId);

        require(
            getPoolId(balancerV2Pool.marketPool) == balancerV2Tokens.marketPoolId,
            "OVLV1Feed: marketPoolId mismatch"
        );

        require(
            getPoolId(balancerV2Pool.ovlWethPool) == balancerV2Tokens.ovlWethPoolId,
            "OVLV1Feed: ovlWethPoolId mismatch"
        );

        // SN TODO: verified the order is token0=dai, token1=weth: now make sure code reflects this
        // specifically when we calculate the reserve in getReserve where we query for the weights
        // we get back [token0 weight, token1 weight]
        // need WETH in market pool to make reserve conversion from ETH => OVL
        address _marketToken0 = address(marketTokens[0]); // DAI
        address _marketToken1 = address(marketTokens[1]); // WETH

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

        (IERC20[] memory ovlWethTokens, , ) = getPoolTokens(balancerV2Tokens.ovlWethPoolId);

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
      address pool,
      IBalancerV2PriceOracle.OracleAverageQuery[] memory queries
    )
    public
    view
    returns (uint256[] memory results)
    {
      IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(pool);
      uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);
      return results;
    }

    function getOracleAverageQuery(
      IBalancerV2PriceOracle.Variable variable,
      uint256 secs,
      uint256 ago
    )
    public view
    returns(IBalancerV2PriceOracle.OracleAverageQuery memory query) {
      IBalancerV2PriceOracle.OracleAverageQuery[] memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
      IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(
        variable,
        secs,
        ago
      );
    }



    /// @notice Returns the time average weighted price corresponding to each of `queries`.
    /// @dev Prices are dev represented as 18 decimal fixed point values.
    /// @dev PAIR_PRICE: the price of the tokens in the Pool, expressed as the price of the second
    /// @dev token in units of the first token. For example, if token A is worth $2, and token B is
    /// @dev worth $4, the pair price will be 2.0. Note that the price is computed *including* the
    /// @dev tokens decimals. This means that the pair price of a Pool with DAI and USDC will be
    /// @dev close to 1.0, despite DAI having 18 decimals and USDC 6.
    function getTimeWeightedAveragePairPrice(
      address pool,
      uint256 secs,
      uint256 ago
    )
    public
    view returns (uint256 result) {
      // address poolWethDai = 0x0b09deA16768f0799065C475bE02919503cB2a35;
      IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(pool);
      IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.PAIR_PRICE;
      // uint256 secs = 1800;
      // uint256 ago = 0;

      IBalancerV2PriceOracle.OracleAverageQuery[] memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
      IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle.OracleAverageQuery(
        variable,
        secs,
        ago
      );
      queries[0] = query;
      uint256[] memory results = priceOracle.getTimeWeightedAverage(queries);
      uint256 result = results[0];
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

    /// @notice Returns pool token information given a pool id
    /// @dev Interfaces the WeightedPool2Tokens contract and calls getPoolTokens
    /// @param balancerV2PoolId pool id
    /// @return The pool's registered tokens
    /// @return Total balances of each token in the pool
    /// @return Most recent block in which any of the pool tokens were updated
    function getPoolTokens(bytes32 balancerV2PoolId)
        public
        view
        returns (
            IERC20[] memory,
            uint256[] memory,
            uint256
        )
    {
        IBalancerV2Vault vault = IBalancerV2Vault(VAULT);
        return vault.getPoolTokens(balancerV2PoolId);
    }

    /// @notice Returns the pool id corresponding to the given pool address
    /// @dev Interfaces with WeightedPool2Tokens contract and calls getPoolId
    /// @param pool Pool address
    /// @return pool id corresponding to the given pool address
    function getPoolId(address pool) public view returns (bytes32) {
        return IBalancerV2Pool(pool).getPoolId();
    }

    /// @notice Returns the normalized weight of the token
    /// @dev Weights are fixed point numbers that sum to FixedPoint.ONE
    /// @dev Ex: a 60 WETH/40 BAL pool returns 400000000000000000, 600000000000000000
    /// @dev Interfaces with the WeightedPool2Tokens contract and calls getNormalizedWeights
    /// @param pool Pool address
    /// @return Normalized pool weights
    function getNormalizedWeights(address pool) public view returns (uint256[] memory) {
        return IBalancerV2Pool(pool).getNormalizedWeights();
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // SN TODO - put just enough code in to get this compiling
        // cache globals for gas savings
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;
        address _marketPool = marketPool;
        address _ovlWethPool = ovlWethPool;

        // // consult to market pool
        // // secondsAgo.length = 4; twaps.length = liqs.length = 3
        // (
        //     uint32[] memory secondsAgos,
        //     uint32[] memory windows,
        //     uint256[] memory nowIdxs
        // ) = _inputsToConsultMarketPool(_microWindow, _macroWindow);
        //

        /* Pair Price Calculations */
        uint256[] memory twaps = getPairPrices();
        uint256 priceOverMicroWindow = twaps[0];
        uint256 priceOverMacroWindow = twaps[1];
        uint256 priceOneMacroWindowAgo = twaps[2];

        /* Reserve Calculations */
        uint256 reserve = getReserve(priceOverMicroWindow);

        return
            Oracle.Data({
                timestamp: block.timestamp,
                microWindow: _microWindow,
                macroWindow: _macroWindow,
                priceOverMicroWindow: priceOverMicroWindow, // secondsAgos = _microWindow
                priceOverMacroWindow: priceOverMacroWindow, // secondsAgos = _macroWindow
                priceOneMacroWindowAgo: priceOneMacroWindowAgo, // secondsAgos = _macroWindow * 2
                reserveOverMicroWindow: reserve,
                hasReserve: true
            });
    }

    /// @dev V = B1 ** w1 * B2 ** w2
    /// @param priceOverMicroWindow price TWAP, P = (B2 / B1) * (w1 / w2)
    function getReserve(uint256 priceOverMicroWindow) public view returns (uint256 reserve) {
      // cache globals for gas savings, SN TODO: verify that this makes a diff here
      address _marketPool = marketPool;
      address _ovlWethPool = ovlWethPool;

      // Retrieve pool weights
      // Ex: a 60 WETH/40 BAL pool returns 400000000000000000, 600000000000000000
      uint256[] memory normalizedWeights = getNormalizedWeights(_marketPool);
      // SN TODO: what if the pool has more than 2 tokens?
      // SN TODO: sanity check that the order the normalized weights are returned are NOT the same
      // order as the return of getPoolId for the market pool. does not impact this code, but still
      // something to note I think
      uint256 weightToken0 = normalizedWeights[0]; // WETH
      uint256 weightToken1 = normalizedWeights[1]; // DAI

      IBalancerV2PriceOracle.Variable variableInvariant = IBalancerV2PriceOracle.Variable.INVARIANT;
      IBalancerV2PriceOracle.OracleAverageQuery[] memory reserveQueries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
      reserveQueries[0] = getOracleAverageQuery(variableInvariant, 600, 0); // for reserve
      // uint256[] memory twaps = getTimeWeightedAverage(_ovlWethPool, reserveQueries);
			uint256[] memory twavs = getTimeWeightedAverage(_marketPool, reserveQueries);

      // B1 represents the WETH reserve over a micro window
      // B1 = [ V / ( (P * w2 / w1) ** w2 ) ] ** [ 1 / (w1 + w2) ]
      uint256 denominator = (priceOverMicroWindow * weightToken1 / weightToken0) ** weightToken1;
      uint256 power = 1 / (weightToken0 + weightToken1);
      uint256 reserveInWeth = (twavs[0] / denominator) ** power;

      (IERC20[] memory ovlWethTokens, uint256[] memory ovlWethBalances, ) = getPoolTokens(ovlWethPoolId);
      // Ensure that the global ovlWethToken0 and ovlWethToken1 are each present in ovlWethTokens
      require(
        address(ovlWethTokens[0]) == ovlWethToken0 || address(ovlWethTokens[1]) == ovlWethToken0,
        "OVLV1Feed: ovlWethToken0 not found"
      );
      require(
        address(ovlWethTokens[1]) == ovlWethToken1 || address(ovlWethTokens[0]) == ovlWethToken1,
        "OVLV1Feed: ovlWethToken1 not found"
      );

      // SN TODO: This only works if two tokens in pool
      uint256 ovlWethBalance0;
      uint256 ovlWethBalance1;
      // uint256 balanceOvlWethToken0;
      // uint256 balanceOvlWethToken1;
      if (address(ovlWethTokens[0]) == ovlWethToken0) {
      // OVL is first in return (expected)
        ovlWethBalance0 = ovlWethBalances[0];
        ovlWethBalance1 = ovlWethBalances[1];
      } else {
      // WETH is first in return
        ovlWethBalance0 = ovlWethBalances[1];
        ovlWethBalance1 = ovlWethBalances[0];
      }

      uint256 reserve = reserveInWeth * (ovlWethBalance0 / ovlWethBalance1);
    }
    
    function getPairPrices() public view returns (uint256[] memory twaps) {
        // cache globals for gas savings, SN TODO: verify that this makes a diff here
        address _marketPool = marketPool;
        /* Pair Price Calculations */
        // SN LEFT OFF HERE
        IBalancerV2PriceOracle.Variable variablePairPrice = IBalancerV2PriceOracle.Variable.PAIR_PRICE;

        IBalancerV2PriceOracle.OracleAverageQuery[] memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](4);
        queries[0] = getOracleAverageQuery(variablePairPrice, 600, 0);
        queries[1] = getOracleAverageQuery(variablePairPrice, 3600, 0);
        queries[2] = getOracleAverageQuery(variablePairPrice, 3600, 3600);

        uint256[] memory twaps = getTimeWeightedAverage(_marketPool, queries);
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
