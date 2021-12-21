// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "./interfaces/IOverlayFeed.sol";
import "./libraries/Oracle.sol";
import "./libraries/Position.sol";
import "./OverlayToken.sol";

contract OverlayMarket {
    using Oracle for Oracle.Data;
    using Position for Position.Info;

    OverlayToken immutable public ovl;
    address public governor;

    // risk params
    uint256 public k; // funding constant
    uint256 public lmbda; // market impact constant
    uint256 public delta; // bid-ask static spread constant
    uint256 public capPayoff; // payoff cap
    uint256 public capOi; // static oi cap
    uint256 public capLeverage; // leverage cap (initial)
    uint256 public maintenanceMargin; // maintenance margin (mm) constant
    uint256 public maintenanceMarginBurnRate; // burn rate for mm constant
    uint256 public tradingFeeRate;

    // trading fee related quantities
    address public tradingFeeRecipient;

    // oracle feeds
    address[2] public feeds;

    // oi related quantities
    uint256 public oiLong;
    uint256 public oiShort;
    uint256 public oiLongShares;
    uint256 public oiShortShares;

    // positions
    Position.Info[] public positions;

    // governor modifier for governance sensitive functions
    modifier onlyGovernor() {
        require(msg.sender == governor, "OVLV1:!governor");
        _;
    }

    constructor(
        address _ovl,
        address[2] memory _feeds,
        uint256 _k,
        uint256 _lmbda,
        uint256 _delta,
        uint256 _capPayoff,
        uint256 _capOi,
        uint256 _capLeverage,
        uint256 _maintenanceMargin,
        uint256 _maintenanceMarginBurnRate,
        uint256 _tradingFeeRate
    ) {
        ovl = OverlayToken(_ovl);
        for (uint256 i=0; i < _feeds.length; i++) {
            feeds[i] = _feeds[i];
        }
        governor = msg.sender;
        tradingFeeRecipient = msg.sender;

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
    }

    /// @dev builds a new position
    function build(
        uint256 collateral,
        uint256 leverage,
        bool isLong,
        uint256 oiMinimum
    ) external returns (uint256 positionId_) {
        Oracle.Data[2] memory data = update();

        // transfer in the OVL collateral needed to back the position
        ovl.transferFrom(msg.sender, address(this), collateral);

        // calculate oi adjusted for fees. fees are taken from collateral
        uint256 oi = collateral * leverage;
        uint256 capOiAdjusted = capOiWithAdjustments(data);
        uint256 impactFee = registerMarketImpact(oi, capOiAdjusted);
        uint256 tradingFee = oi * tradingFeeRate;
        collateral -= impactFee + tradingFee;
        oi = collateral * leverage;

        // add new position's open interest to the side's aggregate oi value
        // and increase number of oi shares issued
        if (isLong) { oiLong += oi; oiLongShares += oi; }
        else { oiShort += oi; oiShortShares += oi; }

        // longs get the ask and shorts get the bid on build
        uint256 price = isLong ? ask(data[0]) : bid(data[0]);

        // store the position info data
        positions.push(Position.Info({
            leverage: leverage,
            isLong: isLong,
            entryPrice: price,
            oiShares: oi,
            debt: oi - collateral,
            cost: collateral
        }));
        positionId_ = positions.length - 1;

        // burn the impact fee and send trading fees to trading fee recipient
        ovl.burn(impactFee);
        ovl.transfer(tradingFeeRecipient, tradingFee);
    }

    /// @dev unwinds shares of an existing position
    function unwind(uint256 positionId, uint256 shares) external {
        Oracle.Data[2] memory data = update();
    }

    /// @dev liquidates a liquidatable position
    function liquidate(uint256 positionId) external {
        Oracle.Data[2] memory data = update();
    }

    /// @dev updates market and fetches freshest data from feeds
    function update() public returns (Oracle.Data[2] memory) {
        payFunding();
        Oracle.Data[2] memory data = getDataFromFeeds();
        return data;
    }

    /// @dev funding payments from overweight oi side to underweight
    function payFunding() public {}

    /// @dev gets latest oracle data from feed
    function getDataFromFeeds() public returns (Oracle.Data[2] memory) {
        Oracle.Data[2] memory data;
        for (uint256 i=0; i < feeds.length; i++) {
            address feed = feeds[i];
            Oracle.Data memory d = IOverlayFeed(feed).latest();
            data[i] = d;
        }
        return data;
    }

    /// @dev gets price quotes for the bid and the ask
    function getPriceQuotes(Oracle.Data memory data) public view returns (uint256 bid_, uint256 ask_) {
        bid_ = bid(data);
        ask_ = ask(data);
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

    /// @dev market impact fee based on open interest proposed for build
    /// @dev and current level of capOi with adjustments
    function registerMarketImpact(uint256 oi, uint256 capOiAdjusted) private returns (uint256) {
        /// TODO: register the impact and return the fee
    }

    /// @dev current open interest cap with adjustments to prevent
    /// @dev front-running trade, back-running trade, and to lower open
    /// @dev interest cap in event we've printed a lot in recent past
    function capOiWithAdjustments(Oracle.Data[2] memory data) public view returns (uint256) {
        uint256 cap = capOi;

        // TODO: apply adjustments

        return cap;
    }

    // TODO: setters for all gov params and associated checks
}
