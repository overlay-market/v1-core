// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "./interfaces/IOverlayV1Feed.sol";
import "./libraries/FixedPoint.sol";
import "./libraries/Oracle.sol";
import "./libraries/Position.sol";
import "./OverlayV1Token.sol";

contract OverlayV1Market {
    using Oracle for Oracle.Data;
    using Position for Position.Info;
    using FixedPoint for uint256;

    uint256 constant internal ONE = 1e18; // 18 decimal places

    OverlayV1Token immutable public ovl; // ovl token
    address immutable public feed; // oracle feed
    address immutable public factory; // factory that deployed this market

    // risk params
    uint256 public k; // funding constant
    uint256 public lmbda; // market impact constant
    uint256 public delta; // bid-ask static spread constant
    uint256 public capPayoff; // payoff cap
    uint256 public capOi; // static oi cap
    uint256 public capLeverage; // initial leverage cap
    uint256 public maintenanceMargin; // maintenance margin (mm) constant
    uint256 public maintenanceMarginBurnRate; // burn rate for mm constant
    uint256 public tradingFeeRate; // trading fee charged on build/unwind
    uint256 public minCollateral; // minimum ovl collateral to open position

    // trading fee related quantities
    address public tradingFeeRecipient;

    // oi related quantities
    uint256 public oiLong;
    uint256 public oiShort;
    uint256 public oiLongShares;
    uint256 public oiShortShares;

    // positions
    Position.Info[] public positions;

    // last call to funding
    uint256 public fundingPaidLast;

    // factory modifier for governance sensitive functions
    modifier onlyFactory() {
        require(msg.sender == factory, "OVLV1: !factory");
        _;
    }

    constructor(
        address _ovl,
        address _feed,
        uint256 _k,
        uint256 _lmbda,
        uint256 _delta,
        uint256 _capPayoff,
        uint256 _capOi,
        uint256 _capLeverage,
        uint256 _maintenanceMargin,
        uint256 _maintenanceMarginBurnRate,
        uint256 _tradingFeeRate,
        uint256 _minCollateral
    ) {
        ovl = OverlayV1Token(_ovl);
        feed = _feed;
        factory = msg.sender;
        tradingFeeRecipient = msg.sender;
        fundingPaidLast = block.timestamp;

        // set the gov params
        k = _k;
        lmbda = _lmbda;
        delta = _delta;
        capPayoff = _capPayoff;
        capOi = _capOi;
        capLeverage = _capLeverage;
        maintenanceMargin = _maintenanceMargin;
        maintenanceMarginBurnRate = _maintenanceMarginBurnRate;
        tradingFeeRate = _tradingFeeRate;
        minCollateral = _minCollateral;
    }

    /// @dev builds a new position
    function build(
        uint256 collateral,
        uint256 leverage,
        bool isLong,
        uint256 minOi
    ) external returns (uint256 positionId_) {
        require(leverage >= ONE, "OVLV1:lev<min");
        require(leverage <= capLeverage, "OVLV1:lev>max");

        Oracle.Data memory data = update();

        // amount of collateral to transfer in to back the position
        uint256 collateralIn = collateral;

        // calculate oi adjusted for fees. fees are taken from collateral
        uint256 oi = collateral.mulUp(leverage);
        uint256 capOiAdjusted = capOiWithAdjustments(data);
        uint256 impactFee = _registerMarketImpact(oi, capOiAdjusted);
        uint256 tradingFee = oi.mulUp(tradingFeeRate);
        collateral -= impactFee + tradingFee;
        oi = collateral.mulUp(leverage);

        require(collateral >= minCollateral, "OVLV1:collateral<min");
        require(oi >= minOi, "OVLV1:oi<min");

        // add new position's open interest to the side's aggregate oi value
        // and increase number of oi shares issued
        if (isLong) {
            oiLong += oi; oiLongShares += oi;
            require(oiLong <= capOiAdjusted, "OVLV1:oi>cap");
        }
        else {
            oiShort += oi; oiShortShares += oi;
            require(oiShort <= capOiAdjusted, "OVLV1:oi>cap");
        }

        // longs get the ask and shorts get the bid on build
        uint256 price = isLong ? ask(data) : bid(data);

        // store the position info data
        // TODO: pack position.info to get gas close to 200k
        positions.push(Position.Info({
            leverage: leverage,
            isLong: isLong,
            entryPrice: price,
            oiShares: oi,
            debt: oi - collateral,
            cost: collateral
        }));
        positionId_ = positions.length - 1;

        // transfer in the OVL collateral needed to back the position
        ovl.transferFrom(msg.sender, address(this), collateralIn);

        // burn the impact fee
        ovl.burn(impactFee);

        // send trading fees to trading fee recipient
        ovl.transfer(tradingFeeRecipient, tradingFee);
    }

    /// @dev unwinds shares of an existing position
    function unwind(uint256 positionId, uint256 shares) external {
        Oracle.Data memory data = update();
    }

    /// @dev liquidates a liquidatable position
    function liquidate(uint256 positionId) external {
        Oracle.Data memory data = update();
    }

    /// @dev updates market and fetches freshest data from feed
    function update() public returns (Oracle.Data memory) {
        payFunding();
        Oracle.Data memory data = IOverlayV1Feed(feed).latest();
        return data;
    }

    /// @dev funding payments from overweight oi side to underweight oi side
    function payFunding() public {
        bool isLongOverweight = oiLong > oiShort;
        uint256 oiOverweight = isLongOverweight ? oiLong : oiShort;
        uint256 oiUnderweight = isLongOverweight ? oiShort : oiLong;
        uint256 oiTotal = oiLong + oiShort;

        // draw down the imbalance by factor of (1-2k)^(t)
        uint256 drawdownFactor = (ONE-2*k).powUp(ONE * (block.timestamp - fundingPaidLast));
        uint256 oiImbalanceNow = drawdownFactor.mulUp(oiOverweight - oiUnderweight);

        if (oiUnderweight == 0) {
            // effectively user pays the protocol if one side has zero oi
            oiOverweight = oiImbalanceNow;
        } else {
            // overweight pays underweight side if oi on both sides
            oiOverweight = (oiTotal + oiImbalanceNow) / 2;
            oiUnderweight = (oiTotal - oiImbalanceNow) / 2;
        }

        oiLong = isLongOverweight ? oiOverweight : oiUnderweight;
        oiShort = isLongOverweight ? oiUnderweight : oiOverweight;
        fundingPaidLast = block.timestamp;
    }

    /// @return next position id
    function nextPositionId() external view returns (uint256) {
        return positions.length;
    }

    /// @dev gets bid price given oracle data
    function bid(Oracle.Data memory data) public view returns (uint256 bid_) {
        bid_ = Math.min(data.priceOverMicroWindow, data.priceOverMacroWindow);
        bid_ -= delta; // approx for e^(-delta) = 1-delta
    }

    /// @dev gets ask price given oracle data
    function ask(Oracle.Data memory data) public view returns (uint256 ask_) {
        ask_ = Math.max(data.priceOverMicroWindow, data.priceOverMacroWindow);
        ask_ += delta; // approx for e^(delta) = 1+delta
    }

    /// @dev gets price quotes for the bid and the ask
    function getPriceQuotes(Oracle.Data memory data) external view returns (uint256 bid_, uint256 ask_) {
        bid_ = bid(data);
        ask_ = ask(data);
    }

    /// @dev current open interest cap with adjustments to prevent
    /// @dev front-running trade, back-running trade, and to lower open
    /// @dev interest cap in event we've printed a lot in recent past
    function capOiWithAdjustments(Oracle.Data memory data) public view returns (uint256) {
        uint256 cap = capOi;

        // TODO: apply adjustments; use linear drift reversion for dynamic
        // instead of rollers to save gas

        return cap;
    }

    /// @dev market impact fee based on open interest proposed for build
    /// @dev and current level of capOi with adjustments
    function _registerMarketImpact(uint256 oi, uint256 capOiAdjusted) private returns (uint256) {
        // TODO: register the impact and return the fee; use linear drift
        // reversion for cumulative impact instead of rollers to save gas
    }

    /// @dev governance adjustable risk parameter setters
    /// @dev bounds checks to risk params imposed at factory level
    /// TODO: checks that parameters are valid (e.g. mm given spread and capLeverage)
    function setK(uint256 _k) external onlyFactory {
        k = _k;
    }

    function setLmbda(uint256 _lmbda) external onlyFactory {
        lmbda = _lmbda;
    }

    function setDelta(uint256 _delta) external onlyFactory {
        delta = _delta;
    }

    function setCapPayoff(uint256 _capPayoff) external onlyFactory {
        capPayoff = _capPayoff;
    }

    function setCapLeverage(uint256 _capLeverage) external onlyFactory {
        capLeverage = _capLeverage;
    }

    function setMaintenanceMargin(uint256 _maintenanceMargin) external onlyFactory {
        maintenanceMargin = _maintenanceMargin;
    }

    function setMaintenanceMarginBurnRate(uint256 _maintenanceMarginBurnRate) external onlyFactory {
        maintenanceMarginBurnRate = _maintenanceMarginBurnRate;
    }

    function setTradingFeeRate(uint256 _tradingFeeRate) external onlyFactory {
        tradingFeeRate = _tradingFeeRate;
    }

    function setMinCollateral(uint256 _minCollateral) external onlyFactory {
        minCollateral = _minCollateral;
    }
}
