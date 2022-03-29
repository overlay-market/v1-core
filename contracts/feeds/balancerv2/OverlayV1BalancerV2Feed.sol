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
        // SN TODO: Check if gas cost is reduced by storing vault in memory
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

    /// @notice Returns the OracleAverageQuery struct containing information for a TWAP query
    /// @dev Builds the OracleAverageQuery struct required to retrieve TWAPs from the
    /// @dev getTimeWeightedAverage function
    /// @param variable Queryable values pertinent to this contract: PAIR_PRICE and INVARIANT
    /// @param secs Duration of TWAP in seconds
    /// @param ago End of TWAP in seconds
    /// @return query Information for a TWAP query
    function getOracleAverageQuery(
        IBalancerV2PriceOracle.Variable variable,
        uint256 secs,
        uint256 ago
    ) public view returns (IBalancerV2PriceOracle.OracleAverageQuery memory) {
        return IBalancerV2PriceOracle.OracleAverageQuery(variable, secs, ago);
    }

    /// @notice Returns the time average weighted price corresponding to each of queries.
    /// @dev Prices are represented as 18 decimal fixed point values.
    /// @dev Interfaces with the WeightedPool2Tokens contract and calls getTimeWeightedAverage
    /// @param pool Pool address
    /// @param queries Information for a time weighted average query
    /// @return Time weighted average price corresponding to each query
    function getTimeWeightedAverage(
        address pool,
        IBalancerV2PriceOracle.OracleAverageQuery[] memory queries
    ) public view returns (uint256[] memory) {
        IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(pool);
        return priceOracle.getTimeWeightedAverage(queries);
    }

    /// @notice Returns the TWAP corresponding to a single query for the price of the tokens in the
    /// @notice pool, expressed as the price of the second token in units of the first token
    /// @dev Prices are dev represented as 18 decimal fixed point values
    /// @dev Variable.PAIR_PRICE is used to construct OracleAverageQuery struct
    /// @param pool Pool address
    /// @param secs Duration of TWAP in seconds
    /// @param ago End of TWAP in seconds
    /// @return result TWAP of tokens in the pool
    function getTimeWeightedAveragePairPrice(
        address pool,
        uint256 secs,
        uint256 ago
    ) public view returns (uint256 result) {
        IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.PAIR_PRICE;

        IBalancerV2PriceOracle.OracleAverageQuery[]
            memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
        IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle
            .OracleAverageQuery(variable, secs, ago);
        queries[0] = query;

        uint256[] memory results = getTimeWeightedAverage(pool, queries);
        uint256 result = results[0];
    }

    /// @notice Returns the TWAI (time weighted average invariant) corresponding to a single query
    /// @notice for the value of the pool's
    /// @notice invariant, which is a measure of its liquidity
    /// @dev Prices are dev represented as 18 decimal fixed point values
    /// @dev Variable.INVARIANT is used to construct OracleAverageQuery struct
    /// @param pool Pool address
    /// @param secs Duration of TWAP in seconds
    /// @param ago End of TWAP in seconds
    /// @return result TWAP of inverse of tokens in pool
    function getTimeWeightedAverageInvariant(
        address pool,
        uint256 secs,
        uint256 ago
    ) public view returns (uint256 result) {
        IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.INVARIANT;

        IBalancerV2PriceOracle.OracleAverageQuery[]
            memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
        IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle
            .OracleAverageQuery(variable, secs, ago);
        queries[0] = query;

        uint256[] memory results = getTimeWeightedAverage(pool, queries);
        uint256 result = results[0];
    }

    /// @notice Returns pool token information given a pool id
    /// @dev Interfaces the WeightedPool2Tokens contract and calls getPoolTokens
    /// @param balancerV2PoolId pool id
    /// @return The pool's registered tokens
    /// @return Total balances of each token in the pool
    /// @return Most recent block in which any of the pool tokens were updated (never used)
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

    /// @dev V = B1 ** w1 * B2 ** w2
    /// @param priceOverMicroWindow price TWAP, P = (B2 / B1) * (w1 / w2)
    function getReserve(uint256 priceOverMicroWindow) public view returns (uint256 reserve) {
        // Cache globals for gas savings, SN TODO: verify that this makes a diff here
        address _marketPool = marketPool;
        address _ovlWethPool = ovlWethPool;

        // Retrieve pool weights
        // Ex: a 60 WETH/40 BAL pool returns 400000000000000000, 600000000000000000
        uint256[] memory normalizedWeights = getNormalizedWeights(_marketPool);
        // SN TODO: what if the pool has more than 2 tokens?
        // SN TODO: sanity check that the order the normalized weights are returned are NOT the
        // same order as the return of getPoolId for the market pool. does not impact this code,
        // but still something to note I think
        uint256 weightToken0 = normalizedWeights[0]; // WETH
        uint256 weightToken1 = normalizedWeights[1]; // DAI

        // SN TODO: Remove hardcode
        uint256 twav = getTimeWeightedAverageInvariant(_marketPool, 600, 0);

        // Want to solve for B2 because if B1 is the expression we want, that means P is B2
        // so B2 = DIA, B1 = WETH
        // account for 2 conditions:
        // 1. if weightToken0 is the market base token (WETH), then we try to get B1
        // 2. if weightToken0 is market quote token (DAI), then we try to get B2
        // could: in normalizedWeights do flip so always WETH first
        // priceOverMicroWindow is laways num quote/num base, the weightToken0 and weightToken1 we
        // get back, could have it where normalizedWeights0 is laways base, and nomarwe1 is always
        // quote so the logic of calculating here is always right (always B1)
        // B1 represents the WETH reserve over a micro window
        // B1 = [ V / ( (P * w2 / w1) ** w2 ) ] ** [ 1 / (w1 + w2) ]
        // SN TODO: use fixedpoint
        // follow mikeys logic by splitting ths out into another function getReserveInWeth, then
        // the logic getRerseveInOvl (that logic below talking about getPairPrice). this makes a
        // call to getReserveInWeth, then gets the reserve number in WETH (B1). getReserveInOvl
        // takes that number and multiplies it by the price in ovlweth
        uint256 denominator = ((priceOverMicroWindow * weightToken1) / weightToken0)**weightToken1;
        // this is going to be 0 (since weights are so large), prob same with denominator
        // the FixedPoint lib
        uint256 power = 1 / (weightToken0 + weightToken1);
        uint256 reserveInWeth = (twav / denominator)**power;

        // NOT right. 1. does not factor in the weigths and really manipulatable because not using
        // TWAP want to do getPairPrices for ovlWethPool
        // I need the TWAP value from ovlWethPool -> getPairPrice with ovlWethPool
        // duplicate getPairPrices -> getOvlWethPrice. keep pairprices but adapt for OVlweth with
        // on query the one query is 600, 0 for micor (only want for micro)
        // only wrinkle is we want to amke sure that the price we are getting is num ETH / num OVL
        // just return what getovlWeithPairPrice

        // DO NOT NEED THIS LINE ANYMORE:
        // uint256 reserve = reserveInWeth * (ovlWethBalance0 / ovlWethBalance1);
        // https://github.com/overlay-market/v1-core/blob/main/contracts/OverlayV1Market.sol#L160
    }

    /// @notice Market pool only (not reserve)
    function getPairPrices() public view returns (uint256[] memory twaps) {
        // cache globals for gas savings, SN TODO: verify that this makes a diff here
        address _marketPool = marketPool;
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;

        /* Pair Price Calculations */
        // SN LEFT OFF HERE
        IBalancerV2PriceOracle.Variable variablePairPrice = IBalancerV2PriceOracle
            .Variable
            .PAIR_PRICE;

        // SN TODO: CHECK: Has this arr initialized at 4, but changed to 3
        IBalancerV2PriceOracle.OracleAverageQuery[]
            memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](3);
        // SN TODO: HARD CODE HERE
        // [Variable enum, seconds, ago]
        // queries[0] = getOracleAverageQuery(variablePairPrice, 600, 0);
        // queries[1] = getOracleAverageQuery(variablePairPrice, 3600, 0);
        // queries[2] = getOracleAverageQuery(variablePairPrice, 3600, 3600);

        // SN TODO: Check if we really need _inputsToConsultMarketPool, or can just use globals
        // SN Q1: Is setting the `queries` array like this the problem?
        // SN Q1: Tried setting it like `SN Q2` but makes no difference
        queries[0] = getOracleAverageQuery(variablePairPrice, microWindow, 0);
        queries[1] = getOracleAverageQuery(variablePairPrice, macroWindow, 0);
        queries[2] = getOracleAverageQuery(variablePairPrice, macroWindow, macroWindow);

        // SN Q2: Tried setting each array entry explicitly, but made no difference
        // IBalancerV2PriceOracle.OracleAverageQuery memory microPairPrice =
        //   getOracleAverageQuery(variablePairPrice, microWindow, 0);
        // queries[0] = microPairPrice;
        // IBalancerV2PriceOracle.OracleAverageQuery memory macroPairPrice =
        //   getOracleAverageQuery(variablePairPrice, macroWindow, 0);
        // queries[0] = macroPairPrice;
        //
        // IBalancerV2PriceOracle.OracleAverageQuery memory macroOneWindowAgoPrice
        //   = getOracleAverageQuery(variablePairPrice, macroWindow, macroWindow);
        // queries[2] = macroOneWindowAgoPrice;

        uint256[] memory twaps = getTimeWeightedAverage(_marketPool, queries);
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // SN TODO - put just enough code in to get this compiling
        // cache globals for gas savings
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;
        address _marketPool = marketPool;
        address _ovlWethPool = ovlWethPool;

        // // SN TODO
        // // consult to market pool
        // // secondsAgo.length = 4; twaps.length = liqs.length = 3
        // (
        //     uint32[] memory secondsAgos,
        //     uint32[] memory windows,
        //     uint256[] memory nowIdxs
        // ) = _inputsToConsultMarketPool(_microWindow, _macroWindow);

        /* Pair Price Calculations */
        uint256[] memory twaps = getPairPrices();
        uint256 priceOverMicroWindow = twaps[0];
        uint256 priceOverMacroWindow = twaps[1];
        uint256 priceOneMacroWindowAgo = twaps[2];

        // uint256 priceOverMicroWindow = 1;
        // uint256 priceOverMacroWindow = 1;
        // uint256 priceOneMacroWindowAgo = 1;

        /* Reserve Calculations */
        // uint256 reserve = getReserve(priceOverMicroWindow);
        uint256 reserve = 1;

        return
            Oracle.Data({
                timestamp: block.timestamp,
                microWindow: _microWindow,
                macroWindow: _macroWindow,
                priceOverMicroWindow: priceOverMicroWindow, // secondsAgos = _microWindow
                priceOverMacroWindow: priceOverMacroWindow, // secondsAgos = _macroWindow
                priceOneMacroWindowAgo: priceOneMacroWindowAgo, // secondsAgos = _macroWindow * 2
                reserveOverMicroWindow: reserve,
                hasReserve: true // only time false if not using a spot AMM (like for chainlink)
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
