// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "./interfaces/IOverlayV1Deployer.sol";
import "./interfaces/IOverlayV1Factory.sol";
import "./interfaces/IOverlayV1Market.sol";
import "./interfaces/IOverlayV1Token.sol";
import "./interfaces/feeds/IOverlayV1FeedFactory.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

import "./libraries/Risk.sol";

import "./OverlayV1Deployer.sol";

contract OverlayV1Factory is IOverlayV1Factory {
    using Risk for uint256[15];

    // risk param bounds
    // NOTE: 1bps = 1e14
    uint256[15] public PARAMS_MIN = [
        0, // MIN_K = 0
        0.01e18, // MIN_LMBDA = 0.01
        0, // MIN_DELTA = 0
        1e18, // MIN_CAP_PAYOFF = 1x
        0, // MIN_CAP_NOTIONAL = 0 OVL
        1e18, // MIN_CAP_LEVERAGE = 1x
        86400, // MIN_CIRCUIT_BREAKER_WINDOW = 1 day
        0, // MIN_CIRCUIT_BREAKER_MINT_TARGET = 0 OVL
        0.01e18, // MIN_MAINTENANCE_MARGIN_FRACTION = 1%
        0.01e18, // MIN_MAINTENANCE_MARGIN_BURN_RATE = 1%
        0.001e18, // MIN_LIQUIDATION_FEE_RATE = 0.10% (10 bps)
        1e14, // MIN_TRADING_FEE_RATE = 0.01% (1 bps)
        0.000_1e18, // MIN_MINIMUM_COLLATERAL = 1e-4 OVL
        0.01e14, // MIN_PRICE_DRIFT_UPPER_LIMIT = 0.01 bps/s
        100 // MIN_AVERAGE_BLOCK_TIME = 0.1s
    ];
    uint256[15] public PARAMS_MAX = [
        0.04e14, // MAX_K = ~ 1000 bps / 8 hr
        10e18, // MAX_LMBDA = 10
        200e14, // MAX_DELTA = 2% (200 bps)
        100e18, // MAX_CAP_PAYOFF = 100x
        88_888_888e18, // MAX_CAP_NOTIONAL = 88,888,888 OVL (initial supply)
        99e18, // MAX_CAP_LEVERAGE = 99x
        31536000, // MAX_CIRCUIT_BREAKER_WINDOW = 365 days
        88_888_888e18, // MAX_CIRCUIT_BREAKER_MINT_TARGET = 88,888,888 OVL (initial supply)
        0.2e18, // MAX_MAINTENANCE_MARGIN_FRACTION = 20%
        0.5e18, // MAX_MAINTENANCE_MARGIN_BURN_RATE = 50%
        0.2e18, // MAX_LIQUIDATION_FEE_RATE = 20.00% (2000 bps)
        100e14, // MAX_TRADING_FEE_RATE = 1% (100 bps)
        100_000e18, // MAX_MINIMUM_COLLATERAL = 100,000 OVL
        1e14, // MAX_PRICE_DRIFT_UPPER_LIMIT = 1 bps/s
        3600000 // MAX_AVERAGE_BLOCK_TIME = 1h (arbitrary but large)
    ];

    // event for risk param updates
    event ParamUpdated(
        address indexed user, address indexed market, Risk.Parameters name, uint256 value
    );

    // event for emergency shutdown
    event EmergencyShutdown(address indexed user, address indexed market);

    // ovl token
    IOverlayV1Token public immutable ovl;

    // market deployer
    IOverlayV1Deployer public immutable deployer;

    // sequencer oracle
    AggregatorV3Interface public sequencerOracle;
    uint256 public gracePeriod;

    // fee related quantities
    address public feeRecipient;

    // registry of supported feed factories
    mapping(address => bool) public isFeedFactory;

    // registry of markets; for a given feed address, returns associated market
    mapping(address => address) public getMarket;

    // registry of deployed markets by factory
    mapping(address => bool) public isMarket;

    // events for factory functions
    event MarketDeployed(address indexed user, address market, address feed);
    event FeedFactoryAdded(address indexed user, address feedFactory);
    event FeedFactoryRemoved(address indexed user, address feedFactory);
    event FeeRecipientUpdated(address indexed user, address recipient);

    // events for sequencer oracle
    event SequencerOracleUpdated(address indexed newOracle);
    event GracePeriodUpdated(uint256 newGracePeriod);

    // governor modifier for governance sensitive functions
    modifier onlyGovernor() {
        require(ovl.hasRole(GOVERNOR_ROLE, msg.sender), "OVLV1: !governor");
        _;
    }

    // governor modifier for governance sensitive functions
    modifier onlyGuardian() {
        require(ovl.hasRole(GUARDIAN_ROLE, msg.sender), "OVLV1: !guardian");
        _;
    }

    // pauser modifier for pausable functions
    modifier onlyPauser() {
        require(ovl.hasRole(PAUSER_ROLE, msg.sender), "OVLV1: !pauser");
        _;
    }

    // risk manager modifier for risk parameters
    modifier onlyRiskManager() {
        require(ovl.hasRole(RISK_MANAGER_ROLE, msg.sender), "OVLV1: !riskManager");
        _;
    }

    constructor(
        address _ovl,
        address _feeRecipient,
        address _sequencerOracle,
        uint256 _gracePeriod
    ) {
        // set ovl
        ovl = IOverlayV1Token(_ovl);

        // set the fee recipient
        _setFeeRecipient(_feeRecipient);

        // create a new deployer to use when deploying markets
        deployer = new OverlayV1Deployer(_ovl);

        // set the sequencer oracle
        sequencerOracle = AggregatorV3Interface(_sequencerOracle);
        _setGracePeriod(_gracePeriod);
    }

    /// @dev adds a supported feed factory
    function addFeedFactory(address feedFactory) external onlyGovernor {
        require(!isFeedFactory[feedFactory], "OVLV1: feed factory already supported");
        isFeedFactory[feedFactory] = true;
        emit FeedFactoryAdded(msg.sender, feedFactory);
    }

    /// @dev removes a supported feed factory
    function removeFeedFactory(address feedFactory) external onlyGovernor {
        require(isFeedFactory[feedFactory], "OVLV1: address not feed factory");
        isFeedFactory[feedFactory] = false;
        emit FeedFactoryRemoved(msg.sender, feedFactory);
    }

    /// @dev deploys a new market contract
    /// @return market_ address of the new market
    function deployMarket(address feedFactory, address feed, uint256[15] calldata params)
        external
        onlyGovernor
        returns (address market_)
    {
        // check feed and feed factory are available for a new market
        _checkFeed(feedFactory, feed);

        // check risk parameters are within bounds
        _checkRiskParams(params);

        // deploy the new market
        market_ = deployer.deploy(feed);

        // initialize the new market
        IOverlayV1Market(market_).initialize(params);

        // grant market mint and burn priveleges on ovl
        ovl.grantRole(MINTER_ROLE, market_);
        ovl.grantRole(BURNER_ROLE, market_);

        // store market registry record for given feed
        // and record address as a deployed market
        getMarket[feed] = market_;
        isMarket[market_] = true;
        emit MarketDeployed(msg.sender, market_, feed);
    }

    /// @notice checks market doesn't exist on feed and feed is from a supported factory
    function _checkFeed(address feedFactory, address feed) private view {
        require(getMarket[feed] == address(0), "OVLV1: market already exists");
        require(isFeedFactory[feedFactory], "OVLV1: feed factory not supported");
        require(IOverlayV1FeedFactory(feedFactory).isFeed(feed), "OVLV1: feed does not exist");
    }

    /// @notice Checks all risk params are within acceptable bounds
    function _checkRiskParams(uint256[15] calldata params) private view {
        uint256 length = params.length;
        for (uint256 i = 0; i < length; i++) {
            _checkRiskParam(Risk.Parameters(i), params[i]);
        }
    }

    /// @notice Checks risk param is within acceptable bounds
    function _checkRiskParam(Risk.Parameters name, uint256 value) private view {
        uint256 minValue = PARAMS_MIN.get(name);
        uint256 maxValue = PARAMS_MAX.get(name);
        require(value >= minValue && value <= maxValue, "OVLV1: param out of bounds");
    }

    /// @notice Setter for per-market risk parameters adjustable by governance
    function setRiskParam(address feed, Risk.Parameters name, uint256 value)
        external
        onlyRiskManager
    {
        _checkRiskParam(name, value);
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setRiskParam(name, value);
        emit ParamUpdated(msg.sender, address(market), name, value);
    }

    /// @notice Setter for fee repository
    function setFeeRecipient(address _feeRecipient) external onlyGovernor {
        _setFeeRecipient(_feeRecipient);
    }

    function _setFeeRecipient(address _feeRecipient) internal {
        require(_feeRecipient != address(0), "OVLV1: feeRecipient should not be zero address");
        feeRecipient = _feeRecipient;
        emit FeeRecipientUpdated(msg.sender, _feeRecipient);
    }

    /// @notice Pause of market by governance in the event of an emergency
    function pause(address feed) external onlyPauser {
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.pause();
    }

    /// @notice Unpause of market by governance in the event of an emergency
    function unpause(address feed) external onlyPauser {
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.unpause();
    }

    /// @notice Shut down of market by governance in the event of an emergency
    function shutdown(address feed) external onlyGuardian {
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.shutdown();
        emit EmergencyShutdown(msg.sender, address(market));
    }

    /**
     * @notice Checks the sequencer oracle is healthy: is up and grace period passed.
     * @return True if the SequencerOracle is up and the grace period passed, false otherwise
     */
    function isUpAndGracePeriodPassed() external view returns (bool) {
        (, int256 answer,, uint256 lastUpdateTimestamp,) = sequencerOracle.latestRoundData();
        return answer == 0 && block.timestamp - lastUpdateTimestamp > gracePeriod;
    }

    function setSequencerOracle(address newSequencerOracle) public onlyGovernor {
        sequencerOracle = AggregatorV3Interface(newSequencerOracle);
        emit SequencerOracleUpdated(newSequencerOracle);
    }

    function setGracePeriod(uint256 newGracePeriod) public onlyGovernor {
        _setGracePeriod(newGracePeriod);
    }

    function _setGracePeriod(uint256 newGracePeriod) internal {
        gracePeriod = newGracePeriod;
        emit GracePeriodUpdated(newGracePeriod);
    }
}
