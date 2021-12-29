// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";
import "./interfaces/IOverlayV1FeedFactory.sol";

import "./OverlayV1Token.sol";
import "./OverlayV1Market.sol";

contract OverlayV1Factory is AccessControlEnumerable {
    bytes32 public constant ADMIN_ROLE = 0x00;
    bytes32 public constant GOVERNOR_ROLE = keccak256("GOVERNOR");

    // risk param bounds
    uint256 public constant MIN_K = 4e8; // ~ 0.1 bps / 8 hr
    uint256 public constant MAX_K = 2e12; // ~ 560 bps / 8 hr
    uint256 public constant MIN_LMBDA = 1e17; // 0.1
    uint256 public constant MAX_LMBDA = 1e19; // 10
    uint256 public constant MIN_DELTA = 1e14; // 0.01% (1 bps)
    uint256 public constant MAX_DELTA = 2e16; // 2% (200 bps)
    uint256 public constant MIN_CAP_PAYOFF = 1e18; // 1x
    uint256 public constant MAX_CAP_PAYOFF = 1e19; // 10x
    uint256 public constant MIN_CAP_LEVERAGE = 1e18; // 1x
    uint256 public constant MAX_CAP_LEVERAGE = 2e19; // 20x
    uint256 public constant MIN_MAINTENANCE_MARGIN = 1e16; // 1%
    uint256 public constant MAX_MAINTENANCE_MARGIN = 2e17; // 20%
    uint256 public constant MIN_MAINTENANCE_MARGIN_BURN_RATE = 1e16; // 1%
    uint256 public constant MAX_MAINTENANCE_MARGIN_BURN_RATE = 5e17; // 50%
    uint256 public constant MIN_TRADING_FEE_RATE = 1e14; // 0.01% (1 bps)
    uint256 public constant MAX_TRADING_FEE_RATE = 3e15; // 0.30% (30 bps)
    uint256 public constant MIN_MINIMUM_COLLATERAL = 1e12; // 1e-6 OVL
    uint256 public constant MAX_MINIMUM_COLLATERAL = 1e18; // 1 OVL

    // events for risk param updates
    event FundingUpdated(address indexed user, uint256 k);
    event ImpactUpdated(address indexed user, uint256 lmbda);
    event BidAskSpreadUpdated(address indexed user, uint256 delta);
    event PayoffCapUpdated(address indexed user, uint256 capPayoff);
    event LeverageCapUpdated(address indexed user, uint256 capLeverage);
    event MaintenanceMarginUpdated(address indexed user, uint256 maintenanceMargin);
    event MaintenanceMarginBurnRateUpdated(address indexed user, uint256 maintenanceMarginBurnRate);
    event TradingFeeRateUpdated(address indexed user, uint256 tradingFeeRate);
    event MinimumCollateralUpdated(address indexed user, uint256 minCollateral);

    // ovl token
    OverlayV1Token immutable public ovl;

    // registry of supported feed factories
    mapping(address => bool) public isFeedFactory;

    // registry of markets; for a given feed address, returns associated market
    mapping(address => address) public getMarket;

    // events for factory functions
    event MarketDeployed(address indexed user, address market, address feed);
    event FeedFactoryAdded(address indexed user, address feedFactory);

    // governor modifier for governance sensitive functions
    modifier onlyGovernor() {
        require(hasRole(GOVERNOR_ROLE, msg.sender), "OVLV1: !governor");
        _;
    }

    constructor(address _ovl) {
        _setupRole(ADMIN_ROLE, msg.sender);
        _setupRole(GOVERNOR_ROLE, msg.sender);

        ovl = OverlayV1Token(_ovl);
    }

    /// @dev adds a supported feed factory
    function addFeedFactory(address feedFactory) external onlyGovernor {
        require(!isFeedFactory[feedFactory], "OVLV1: feed factory already supported");
        isFeedFactory[feedFactory] = true;
        emit FeedFactoryAdded(msg.sender, feedFactory);
    }

    /// @dev deploys a new market contract
    /// @return market_ address of the new market
    function deployMarket(
        address feedFactory,
        address feed,
        uint256 k,
        uint256 lmbda,
        uint256 delta,
        uint256 capPayoff,
        uint256 capOi,
        uint256 capLeverage,
        uint256 maintenanceMargin,
        uint256 maintenanceMarginBurnRate,
        uint256 tradingFeeRate,
        uint256 minCollateral
    ) external onlyGovernor returns (address market_) {
        require(getMarket[feed] == address(0), "OVLV1: market already exists");
        require(isFeedFactory[feedFactory], "OVLV1: feed factory not supported");
        require(IOverlayV1FeedFactory(feedFactory).isFeed(), "OVLV1: feed does not exist");

        // Use the CREATE2 opcode to deploy a new Market contract.
        // Will revert if market which accepts feed in its constructor has already
        // been deployed since salt would be the same and can't deploy with it twice.
        market_ = address(new OverlayV1Market{salt: keccak256(abi.encode(feed))}(
            address(ovl),
            feed,
            k,
            lmbda,
            delta,
            capPayoff,
            capOi,
            capLeverage,
            maintenanceMargin,
            maintenanceMarginBurnRate,
            tradingFeeRate,
            minCollateral
        ));

        // grant market mint and burn priveleges on ovl
        ovl.grantRole(ovl.MINTER_ROLE(), market_);
        ovl.grantRole(ovl.BURNER_ROLE(), market_);

        getMarket[feed] = market_;
        emit MarketDeployed(msg.sender, market_, feed);
    }

    /// below are per-market risk parameter setters,
    /// adjustable by governance

    /// @dev funding parameter setter
    function setK(address feed, uint256 k) external onlyGovernor {
        require(k >= MIN_K && k <= MAX_K, "OVLV1: k out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setK(k);
        emit FundingUpdated(msg.sender, k);
    }

    /// @dev market impact parameter setter
    function setLmbda(address feed, uint256 lmbda) external onlyGovernor {
        require(lmbda >= MIN_LMBDA && lmbda <= MAX_LMBDA, "OVLV1: lmbda out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setLmbda(lmbda);
        emit ImpactUpdated(msg.sender, lmbda);
    }

    /// @dev bid-ask spread setter
    function setDelta(address feed, uint256 delta) external onlyGovernor {
        require(delta >= MIN_DELTA && delta <= MAX_DELTA, "OVLV1: delta out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setDelta(delta);
        emit BidAskSpreadUpdated(msg.sender, delta);
    }

    /// @dev payoff cap setter
    function setCapPayoff(address feed, uint256 capPayoff) external onlyGovernor {
        require(capPayoff >= MIN_CAP_PAYOFF && capPayoff <= MAX_CAP_PAYOFF, "OVLV1: capPayoff out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setCapPayoff(capPayoff);
        emit PayoffCapUpdated(msg.sender, capPayoff);
    }

    /// @dev initial leverage cap setter
    function setCapLeverage(address feed, uint256 capLeverage) external onlyGovernor {
        require(capLeverage >= MIN_CAP_LEVERAGE && capLeverage <= MAX_CAP_LEVERAGE, "OVLV1: capLeverage out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setCapLeverage(capLeverage);
        emit LeverageCapUpdated(msg.sender, capLeverage);
    }

    /// @dev maintenance margin setter
    function setMaintenanceMargin(address feed, uint256 maintenanceMargin) external onlyGovernor {
        require(maintenanceMargin >= MIN_MAINTENANCE_MARGIN && maintenanceMargin <= MAX_MAINTENANCE_MARGIN, "OVLV1: maintenanceMargin out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setMaintenanceMargin(maintenanceMargin);
        emit MaintenanceMarginUpdated(msg.sender, maintenanceMargin);
    }

    /// @dev burn % of maintenance margin on liquidation setter
    function setMaintenanceMarginBurnRate(address feed, uint256 maintenanceMarginBurnRate) external onlyGovernor {
        require(maintenanceMarginBurnRate >= MIN_MAINTENANCE_MARGIN_BURN_RATE && maintenanceMarginBurnRate <= MAX_MAINTENANCE_MARGIN_BURN_RATE, "OVLV1: maintenanceMarginBurnRate out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setMaintenanceMarginBurnRate(maintenanceMarginBurnRate);
        emit MaintenanceMarginBurnRateUpdated(msg.sender, maintenanceMarginBurnRate);
    }

    /// @dev trading fee % setter
    function setTradingFeeRate(address feed, uint256 tradingFeeRate) external onlyGovernor {
        require(tradingFeeRate >= MIN_TRADING_FEE_RATE && tradingFeeRate <= MAX_TRADING_FEE_RATE, "OVLV1: tradingFeeRate out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setTradingFeeRate(tradingFeeRate);
        emit TradingFeeRateUpdated(msg.sender, tradingFeeRate);
    }

    /// @dev minimum collateral to build position setter
    function setMinCollateral(address feed, uint256 minCollateral) external onlyGovernor {
        require(minCollateral >= MIN_MINIMUM_COLLATERAL && minCollateral <= MAX_MINIMUM_COLLATERAL, "OVLV1: minCollateral out of bounds");
        OverlayV1Market market = OverlayV1Market(getMarket[feed]);
        market.setMinCollateral(minCollateral);
        emit MinimumCollateralUpdated(msg.sender, minCollateral);
    }
}
