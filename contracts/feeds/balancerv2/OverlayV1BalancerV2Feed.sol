// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../OverlayV1Feed.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2Pool.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2Vault.sol";
import "../../interfaces/feeds/balancerv2/IBalancerV2PriceOracle.sol";
import "../../interfaces/feeds/balancerv2/IOverlayV1BalancerV2Feed.sol";
import "../../libraries/balancerv2/BalancerV2Tokens.sol";
import "../../libraries/balancerv2/BalancerV2PoolInfo.sol";
import "../../libraries/FixedPoint.sol";

contract OverlayV1BalancerV2Feed is IOverlayV1BalancerV2Feed, OverlayV1Feed {
    using FixedPoint for uint256;

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
        (IERC20[] memory marketTokens, , ) = getPoolTokens(balancerV2Tokens.marketPoolId);

        require(
            getPoolId(balancerV2Pool.marketPool) == balancerV2Tokens.marketPoolId,
            "OVLV1Feed: marketPoolId mismatch"
        );

        require(
            getPoolId(balancerV2Pool.ovlWethPool) == balancerV2Tokens.ovlWethPoolId,
            "OVLV1Feed: ovlWethPoolId mismatch"
        );

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

    /// @notice Returns the time average weighted price corresponding to each of queries
    /// @dev Prices are represented as 18 decimal fixed point values.
    /// @dev Interfaces with the WeightedPool2Tokens contract and calls getTimeWeightedAverage
    /// @param pool Pool address
    /// @param queries Information for a time weighted average query
    /// @return twaps_ Time weighted average price corresponding to each query
    function getTimeWeightedAverage(
        address pool,
        IBalancerV2PriceOracle.OracleAverageQuery[] memory queries
    ) public view returns (uint256[] memory twaps_) {
        IBalancerV2PriceOracle priceOracle = IBalancerV2PriceOracle(pool);
        twaps_ = priceOracle.getTimeWeightedAverage(queries);
    }

    /// @notice Returns the TWAI (time weighted average invariant) corresponding to a single query
    /// @notice for the value of the pool's
    /// @notice invariant, which is a measure of its liquidity
    /// @dev Prices are dev represented as 18 decimal fixed point values
    /// @dev Variable.INVARIANT is used to construct OracleAverageQuery struct
    /// @param pool Pool address
    /// @param secs Duration of TWAP in seconds
    /// @param ago End of TWAP in seconds
    /// @return result_ TWAP of inverse of tokens in pool
    function getTimeWeightedAverageInvariant(
        address pool,
        uint256 secs,
        uint256 ago
    ) public view returns (uint256 result_) {
        IBalancerV2PriceOracle.Variable variable = IBalancerV2PriceOracle.Variable.INVARIANT;

        IBalancerV2PriceOracle.OracleAverageQuery[]
            memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);
        IBalancerV2PriceOracle.OracleAverageQuery memory query = IBalancerV2PriceOracle
            .OracleAverageQuery(variable, secs, ago);
        queries[0] = query;

        uint256[] memory results = getTimeWeightedAverage(pool, queries);
        result_ = results[0];
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
    /// @return poolId_ pool id corresponding to the given pool address
    function getPoolId(address pool) public view returns (bytes32 poolId_) {
        poolId_ = IBalancerV2Pool(pool).getPoolId();
    }

    /// @notice Returns the normalized weight of the token
    /// @dev Weights are fixed point numbers that sum to FixedPoint.ONE
    /// @dev Ex: a 60 WETH/40 DAI pool returns [400000000000000000 DAI, 600000000000000000 WETH]
    /// @dev Interfaces with the WeightedPool2Tokens contract and calls getNormalizedWeights
    /// @param pool Pool address
    /// @return weights_ Normalized pool weights
    function getNormalizedWeights(address pool) public view returns (uint256[] memory weights_) {
        weights_ = IBalancerV2Pool(pool).getNormalizedWeights();
    }

    /// @dev V = B1 ** w1 * B2 ** w2
    /// @param priceOverMicroWindow price TWAP, P = (B2 / B1) * (w1 / w2)
    function getReserve(uint256 priceOverMicroWindow) public view returns (uint256 reserve_) {
        // Cache globals for gas savings, SN TODO: verify that this makes a diff here
        address _marketPool = marketPool;
        address _ovlWethPool = ovlWethPool;
        uint256 _microWindow = microWindow;

        uint256 twav = getTimeWeightedAverageInvariant(_marketPool, _microWindow, 0);
        uint256 reserveInWeth = getReserveInWeth(twav, priceOverMicroWindow); // units WETH

        uint256 ovlWethPairPrice = getPairPriceOvlWeth();
        // for gas: do them all in the constructor
        // can store marketToken0/1, and ovlWethToken0
        // /then pull from storage if ovWethToken0 == WETH
        // could store bool and have check in constuctor
        // if OVL is base (token1) then OVL/WETH price is #weth/#ovl
        // reserve_ = reserveInWeth.divUp(ovlWethPairPrice);
        // if OVL is quote (token0) then OVL/WETH price is #ovl/#weth
        reserve_ = reserveInWeth.mulUp(ovlWethPairPrice);
    }

    /// @notice Gets reserve in WETH
    /// @dev https://oips.overlay.market/notes/note-10
    /// @dev k: token index, only two-token pools are used in the Balancer V2 WeightedPool2Tokens
    /// @dev contract
    /// @dev B_k: number of k type tokens in the pool
    /// @dev w_k: weight for k type tokens in the pool, Σ_k w_k = 1
    /// @dev Invariant for the spot pool for a two token pool: V = (B_0 ** w_0) * (B_1 ** w_1)
    /// @dev Spot price inferred from the relative number of tokens in pool:
    /// @dev P = (B_1 / B_0) * (w_0 / w_1)
    /// @dev Assume: (w_0 + w_1) = 1 => so (1 / (w_0 + w_1)) = 1
    /// @dev If the base token (marketToken0) is WETH, solve for B_0 using equations V and P:
    /// @dev B_0 = [ twav * (priceOverMicroWindow * w_0 / w_1) ** w_1 ] ** (1 / (w_0 + w_1))
    /// @dev B_0 = [ twav * (priceOverMicroWindow * w_0 / w_1) ** w_1 ] ** (1 / 1)
    /// @dev If the quote token (marketToken1) is WETH, solve for B_1 using equations V and P
    /// @dev B_1 = [ twav / (priceOverMicroWindow * w_1 / w_0) ** w_1 ] ** (1 / (w_0 + w_1))
    /// @dev B_1 = [ twav / (priceOverMicroWindow * w_1 / w_0) ** w_1 ] ** (1 / 1)
    /// @param twav Time weighted average invariant
    /// @param priceOverMicroWindow TWAP over last micro window
    /// @return reserveInWeth_ reserve in WETH
    function getReserveInWeth(uint256 twav, uint256 priceOverMicroWindow)
        public
        view
        returns (uint256 reserveInWeth_)
    {
        // Retrieve pool weights
        // Ex: a 60 WETH/40 DAI pool returns [400000000000000000 DAI, 600000000000000000 WETH]
        uint256[] memory normalizedWeights = getNormalizedWeights(marketPool);

        // WeightedPool2Tokens contract only ever has two pools
        uint256 weightToken0 = normalizedWeights[0]; // DAI
        uint256 weightToken1 = normalizedWeights[1]; // WETH
        uint256 denominator;
        // If marketToken0 (the base token) is WETH, solve for B0
        // If marketToken1 (the quote token) is WETH, solve for B1
        if (marketToken0 == WETH) {
            /// B_0 = [ twav * (priceOverMicroWindow * w_0 / w_1) ** w_0 ]
            denominator = (priceOverMicroWindow.mulUp(weightToken0).divUp(weightToken1)).powUp(
                weightToken0
            );
        } else if (marketToken1 == WETH) {
            /// B_1 = [ twav / (priceOverMicroWindow * w_1 / w_0) ** w_1 ]
            denominator = (priceOverMicroWindow.mulUp(weightToken1).divUp(weightToken0)).powUp(
                weightToken1
            );
        } else {
            revert("OVLV!: WETH not a market token");
        }
        uint256 power = uint256(1).divUp(weightToken0.add(weightToken1));
        reserveInWeth_ = twav.divUp(denominator).powUp(power);
    }

    /// @notice Market pool only (not reserve)
    function getPairPriceOvlWeth() public view returns (uint256 twap_) {
        // cache globals for gas savings, SN TODO: verify that this makes a diff here
        address _ovlWethPool = ovlWethPool;
        uint256 _microWindow = microWindow;

        /* Pair Price Calculations */
        IBalancerV2PriceOracle.Variable variablePairPrice = IBalancerV2PriceOracle
            .Variable
            .PAIR_PRICE;

        IBalancerV2PriceOracle.OracleAverageQuery[]
            memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](1);

        // [Variable enum, seconds, ago]
        queries[0] = getOracleAverageQuery(variablePairPrice, microWindow, 0);

        uint256[] memory twaps = getTimeWeightedAverage(_ovlWethPool, queries);
        twap_ = twaps[0];
    }

    /// @notice Market pool only (not reserve)
    function getPairPrices() public view returns (uint256[] memory twaps_) {
        // cache globals for gas savings, SN TODO: verify that this makes a diff here
        address _marketPool = marketPool;
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;

        /* Pair Price Calculations */
        IBalancerV2PriceOracle.Variable variablePairPrice = IBalancerV2PriceOracle
            .Variable
            .PAIR_PRICE;

        IBalancerV2PriceOracle.OracleAverageQuery[]
            memory queries = new IBalancerV2PriceOracle.OracleAverageQuery[](3);

        // [Variable enum, seconds, ago]
        queries[0] = getOracleAverageQuery(variablePairPrice, microWindow, 0);
        queries[1] = getOracleAverageQuery(variablePairPrice, macroWindow, 0);
        queries[2] = getOracleAverageQuery(variablePairPrice, macroWindow, macroWindow);

        twaps_ = getTimeWeightedAverage(_marketPool, queries);
    }

    function _fetch() internal view virtual override returns (Oracle.Data memory) {
        // SN TODO - put just enough code in to get this compiling
        // cache globals for gas savings
        uint256 _microWindow = microWindow;
        uint256 _macroWindow = macroWindow;
        address _marketPool = marketPool;
        address _ovlWethPool = ovlWethPool;

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
                hasReserve: true // only time false if not using a spot AMM (like for chainlink)
            });
    }
}
