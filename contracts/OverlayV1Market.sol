// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "./interfaces/IOverlayV1Feed.sol";
import "./libraries/FixedPoint.sol";
import "./libraries/Oracle.sol";
import "./libraries/Position.sol";
import "./libraries/Roller.sol";
import "./OverlayV1Token.sol";

contract OverlayV1Market {
    using FixedPoint for uint256;
    using Oracle for Oracle.Data;
    using Position for mapping(bytes32 => Position.Info);
    using Position for Position.Info;
    using Roller for Roller.Snapshot;

    uint256 internal constant ONE = 1e18; // 18 decimal places
    uint256 internal constant AVERAGE_BLOCK_TIME = 14; // (BAD) TODO: remove since not futureproof

    // cap for euler exponent powers; SEE: ./libraries/LogExpMath.sol::pow
    uint256 internal constant MAX_NATURAL_EXPONENT = 41e18;
    uint256 internal constant EULER = 2718281828459045091; // 2.71828e18
    uint256 internal constant INVERSE_EULER = 367879441171442334; // 0.367879e18

    OverlayV1Token public immutable ovl; // ovl token
    address public immutable feed; // oracle feed
    address public immutable factory; // factory that deployed this market

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

    // rollers
    Roller.Snapshot public snapshotVolumeBid; // snapshot of recent volume on bid
    Roller.Snapshot public snapshotVolumeAsk; // snapshot of recent volume on ask
    Roller.Snapshot public snapshotMinted; // snapshot of recent PnL minted/burned

    // positions
    mapping(bytes32 => Position.Info) public positions;
    uint256 private _totalPositions;

    // last call to funding
    uint256 public timestampFundingLast;

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
        timestampFundingLast = block.timestamp;

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
        bool isLong
    ) external returns (uint256 positionId_) {
        require(leverage >= ONE, "OVLV1:lev<min");
        require(leverage <= capLeverage, "OVLV1:lev>max");
        require(collateral >= minCollateral, "OVLV1:collateral<min");

        Oracle.Data memory data = update();

        // calculate oi and fees. fees are added to collateral needed to
        // transfer in to back a position
        uint256 oi = collateral.mulUp(leverage);
        uint256 capOiAdjusted = capOiWithAdjustments(data);
        uint256 tradingFee = oi.mulUp(tradingFeeRate);

        // amount of collateral to transfer in + fees
        uint256 collateralIn = collateral + tradingFee;

        // add new position's open interest to the side's aggregate oi value
        // and increase number of oi shares issued
        if (isLong) {
            oiLong += oi;
            oiLongShares += oi;
            require(oiLong <= capOiAdjusted, "OVLV1:oi>cap");
        } else {
            oiShort += oi;
            oiShortShares += oi;
            require(oiShort <= capOiAdjusted, "OVLV1:oi>cap");
        }

        // longs get the ask and shorts get the bid on build
        // register the additional volume taking either the ask or bid
        // TODO: pack snapshotVolumes to get gas close to 200k
        // TODO: add maxSlippage input param to bid(), ask()
        uint256 volume = isLong
            ? _registerVolumeAsk(data, oi, capOiAdjusted)
            : _registerVolumeBid(data, oi, capOiAdjusted);
        uint256 price = isLong ? ask(data, volume) : bid(data, volume);

        // store the position info data
        // TODO: pack position.info to get gas close to 200k
        positionId_ = _totalPositions;
        positions.set(msg.sender, positionId_, Position.Info({
            leverage: leverage,
            isLong: isLong,
            entryPrice: price,
            oiShares: oi,
            debt: oi - collateral,
            cost: collateral
        }));
        _totalPositions++;

        // transfer in the OVL collateral needed to back the position
        ovl.transferFrom(msg.sender, address(this), collateralIn);

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
        uint256 drawdownFactor = (ONE - 2 * k).powUp(
            ONE * (block.timestamp - timestampFundingLast)
        );
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
        timestampFundingLast = block.timestamp;
    }

    /// @return next position id
    function nextPositionId() external view returns (uint256) {
        return _totalPositions;
    }

    /// @dev current open interest cap with adjustments to prevent
    /// @dev front-running trade, back-running trade, and to lower open
    /// @dev interest cap in event we've printed a lot in recent past
    function capOiWithAdjustments(Oracle.Data memory data) public view returns (uint256) {
        uint256 cap = capOi;

        // Adjust cap downward if exceeds bounds from front run attack
        cap = Math.min(cap, capOiFrontRunBound(data));

        // Adjust cap downward if exceeds bounds from back run attack
        cap = Math.min(cap, capOiBackRunBound(data));

        // TODO: adjust cap downward for circuit breaker

        return cap;
    }

    /// @dev bound on open interest cap to mitigate front-running attack
    /// @dev bound = lmbda * reserveInOvl / 2
    function capOiFrontRunBound(Oracle.Data memory data) public view returns (uint256) {
        if (!data.hasReserve) {
            return capOi;
        }
        return lmbda.mulDown(data.reserveOverMicroWindow).divDown(2 * ONE);
    }

    /// @dev bound on open interest cap to mitigate back-running attack
    /// @dev bound = macroWindow * reserveInOvl * 2 * delta
    function capOiBackRunBound(Oracle.Data memory data) public view returns (uint256) {
        if (!data.hasReserve) {
            return capOi;
        }

        // TODO: macroWindow should be in blocks in current spec. What to do here to be
        // futureproof vs having an average block time constant (BAD)
        uint256 window = (data.macroWindow * ONE) / AVERAGE_BLOCK_TIME;
        return delta.mulDown(data.reserveOverMicroWindow).mulDown(window).mulDown(2 * ONE);
    }

    /// @dev gets bid price given oracle data and recent volume for market impact
    function bid(Oracle.Data memory data, uint256 volume) public view returns (uint256 bid_) {
        bid_ = Math.min(data.priceOverMicroWindow, data.priceOverMacroWindow);

        uint256 pow = delta + lmbda.mulUp(volume);
        require(pow <= MAX_NATURAL_EXPONENT, "OVLV1:slippage>max");

        bid_ = bid_.mulDown(INVERSE_EULER.powUp(pow));
    }

    /// @dev gets ask price given oracle data and recent volume for market impact
    function ask(Oracle.Data memory data, uint256 volume) public view returns (uint256 ask_) {
        ask_ = Math.max(data.priceOverMicroWindow, data.priceOverMacroWindow);

        uint256 pow = delta + lmbda.mulUp(volume);
        require(pow <= MAX_NATURAL_EXPONENT, "OVLV1:slippage>max");

        ask_ = ask_.mulUp(EULER.powUp(pow));
    }

    /**
      @dev Rolling volume adjustments on bid side to be used for market impact.
      @dev Volume values are normalized with respect to oi cap.
     **/
    function _registerVolumeBid(
        Oracle.Data memory data,
        uint256 oi,
        uint256 capOiAdjusted
    ) private returns (uint256) {
        // save gas with snapshot in memory
        Roller.Snapshot memory snapshot = snapshotVolumeBid;
        int256 value = int256(oi.divUp(capOiAdjusted));

        // calculates the decay in the rolling volume since last snapshot
        // and determines new window to decay over
        snapshot = snapshot.transform(block.timestamp, data.microWindow, value);

        // store the transformed snapshot
        snapshotVolumeBid = snapshot;

        // return the volume
        uint256 volume = uint256(snapshot.accumulator);
        return volume;
    }

    /**
      @dev Rolling volume adjustments on ask side to be used for market impact.
      @dev Volume values are normalized with respect to oi cap.
     **/
    function _registerVolumeAsk(
        Oracle.Data memory data,
        uint256 oi,
        uint256 capOiAdjusted
    ) private returns (uint256) {
        // save gas with snapshot in memory
        Roller.Snapshot memory snapshot = snapshotVolumeAsk;
        int256 value = int256(oi.divUp(capOiAdjusted));

        // calculates the decay in the rolling volume since last snapshot
        // and determines new window to decay over
        snapshot = snapshot.transform(block.timestamp, data.microWindow, value);

        // store the transformed snapshot
        snapshotVolumeAsk = snapshot;

        // return the volume
        uint256 volume = uint256(snapshot.accumulator);
        return volume;
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

    function setCapOi(uint256 _capOi) external onlyFactory {
        capOi = _capOi;
    }

    function setCapLeverage(uint256 _capLeverage) external onlyFactory {
        capLeverage = _capLeverage;
    }

    function setMaintenanceMargin(uint256 _maintenanceMargin) external onlyFactory {
        maintenanceMargin = _maintenanceMargin;
    }

    function setMaintenanceMarginBurnRate(uint256 _maintenanceMarginBurnRate)
        external
        onlyFactory
    {
        maintenanceMarginBurnRate = _maintenanceMarginBurnRate;
    }

    function setTradingFeeRate(uint256 _tradingFeeRate) external onlyFactory {
        tradingFeeRate = _tradingFeeRate;
    }

    function setMinCollateral(uint256 _minCollateral) external onlyFactory {
        minCollateral = _minCollateral;
    }
}
