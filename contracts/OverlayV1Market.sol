// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "./interfaces/IOverlayV1Market.sol";
import "./interfaces/IOverlayV1Token.sol";
import "./interfaces/feeds/IOverlayV1Feed.sol";

import "./libraries/FixedPoint.sol";
import "./libraries/Oracle.sol";
import "./libraries/Position.sol";
import "./libraries/Risk.sol";
import "./libraries/Roller.sol";

contract OverlayV1Market is IOverlayV1Market {
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

    // immutables
    IOverlayV1Token public immutable ovl; // ovl token
    address public immutable feed; // oracle feed
    address public immutable factory; // factory that deployed this market

    // risk params
    uint256 public k; // funding constant
    uint256 public lmbda; // market impact constant
    uint256 public delta; // bid-ask static spread constant
    uint256 public capPayoff; // payoff cap
    uint256 public capOi; // static oi cap
    uint256 public capLeverage; // initial leverage cap
    uint256 public circuitBreakerWindow; // trailing window for circuit breaker
    uint256 public circuitBreakerMintTarget; // target mint rate for circuit breaker
    uint256 public maintenanceMargin; // maintenance margin (mm) constant
    uint256 public maintenanceMarginBurnRate; // burn rate for mm constant
    uint256 public tradingFeeRate; // trading fee charged on build/unwind
    uint256 public minCollateral; // minimum ovl collateral to open position
    uint256 public priceDriftUpperLimit; // upper limit for feed price changes

    // trading fee related quantities
    address public tradingFeeRecipient;

    // oi related quantities
    uint256 public oiLong;
    uint256 public oiShort;
    uint256 public oiLongShares;
    uint256 public oiShortShares;

    // rollers
    Roller.Snapshot public override snapshotVolumeBid; // snapshot of recent volume on bid
    Roller.Snapshot public override snapshotVolumeAsk; // snapshot of recent volume on ask
    Roller.Snapshot public override snapshotMinted; // snapshot of recent PnL minted/burned

    // positions
    mapping(bytes32 => Position.Info) public override positions;
    uint256 private _totalPositions;

    // data from last call to update
    uint256 public timestampUpdateLast;

    // factory modifier for governance sensitive functions
    modifier onlyFactory() {
        require(msg.sender == factory, "OVLV1: !factory");
        _;
    }

    // events for core functions
    event Build(
        address indexed sender, // address that initiated build
        uint256 positionId, // id of built position
        uint256 oi, // oi of position at build
        uint256 debt, // debt of position at build
        bool isLong, // whether is long or short
        uint256 price // entry price
    );
    event Unwind(
        address indexed sender, // address that initiated unwind
        uint256 positionId, // id of unwound position
        uint256 fraction, // fraction of position unwound
        int256 mint, // total amount minted/burned (+/-) at unwind
        uint256 price // exit price
    );
    event Liquidate(
        address indexed sender, // address that initiated liquidate
        address indexed owner, // address that owned the liquidated position
        uint256 positionId, // id of the liquidated position
        int256 mint, // total amount burned (-) at liquidate
        uint256 price // liquidation price
    );

    constructor(
        address _ovl,
        address _feed,
        address _factory,
        Risk.Params memory params
    ) {
        ovl = IOverlayV1Token(_ovl);
        feed = _feed;
        factory = _factory;
        tradingFeeRecipient = _factory; // TODO: disburse trading fees in factory

        // initialize update data
        // TODO: test
        Oracle.Data memory data = IOverlayV1Feed(feed).latest();
        require(mid(data, 0, 0) > 0, "OVLV1:!data");
        timestampUpdateLast = block.timestamp;

        // set the gov params
        k = params.k;
        lmbda = params.lmbda;
        delta = params.delta;
        capPayoff = params.capPayoff;
        capOi = params.capOi;
        capLeverage = params.capLeverage;
        circuitBreakerWindow = params.circuitBreakerWindow;
        circuitBreakerMintTarget = params.circuitBreakerMintTarget;
        maintenanceMargin = params.maintenanceMargin;
        maintenanceMarginBurnRate = params.maintenanceMarginBurnRate;
        tradingFeeRate = params.tradingFeeRate;
        minCollateral = params.minCollateral;
        priceDriftUpperLimit = params.priceDriftUpperLimit;
    }

    /// @dev builds a new position
    function build(
        uint256 collateral,
        uint256 leverage,
        bool isLong,
        uint256 priceLimit
    ) external returns (uint256 positionId_) {
        require(leverage >= ONE, "OVLV1:lev<min");
        require(leverage <= capLeverage, "OVLV1:lev>max");
        require(collateral >= minCollateral, "OVLV1:collateral<min");

        // call to update before any effects
        Oracle.Data memory data = update();

        // calculate oi and fees. fees are added to collateral needed
        // to back a position
        uint256 oi = collateral.mulUp(leverage);
        uint256 tradingFee = oi.mulUp(tradingFeeRate);

        // calculate current oi cap adjusted circuit breaker *then* adjust
        // for front run and back run bounds (order matters)
        // TODO: test for ordering
        uint256 capOiAdjusted = capOiAdjustedForCircuitBreaker(capOi);
        capOiAdjusted = capOiAdjustedForBounds(data, capOiAdjusted);

        // longs get the ask and shorts get the bid on build
        // register the additional volume on either the ask or bid
        uint256 volume = isLong
            ? _registerVolumeAsk(data, oi, capOiAdjusted)
            : _registerVolumeBid(data, oi, capOiAdjusted);
        uint256 price = isLong ? ask(data, volume) : bid(data, volume);
        // check price hasn't changed more than max slippage specified by trader
        require(isLong ? price <= priceLimit : price >= priceLimit, "OVLV1:slippage>max");

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

        // store the position info data
        positionId_ = _totalPositions;
        positions.set(
            msg.sender,
            positionId_,
            Position.Info({
                oiShares: uint120(oi), // won't overflow as capOi max is 8e24
                debt: uint120(oi - collateral),
                isLong: isLong,
                liquidated: false,
                entryPrice: price
            })
        );
        _totalPositions++;

        // emit build event
        emit Build(msg.sender, positionId_, oi, oi - collateral, isLong, price);

        // transfer in the OVL collateral needed to back the position + fees
        ovl.transferFrom(msg.sender, address(this), collateral + tradingFee);

        // send trading fees to trading fee recipient
        ovl.transfer(tradingFeeRecipient, tradingFee);
    }

    /// @dev unwinds fraction of an existing position
    function unwind(
        uint256 positionId,
        uint256 fraction,
        uint256 priceLimit
    ) external {
        require(fraction > 0, "OVLV1:fraction<min");
        require(fraction <= ONE, "OVLV1:fraction>max");

        // check position exists
        Position.Info memory pos = positions.get(msg.sender, positionId);
        require(pos.exists(), "OVLV1:!position");

        // call to update before any effects
        Oracle.Data memory data = update();

        // cache for gas savings
        uint256 totalOi = pos.isLong ? oiLong : oiShort;
        uint256 totalOiShares = pos.isLong ? oiLongShares : oiShortShares;

        // longs get the bid and shorts get the ask on unwind
        // register the additional volume on either the ask or bid
        // current oi cap only adjusted for bounds (no circuit breaker so traders
        // don't get stuck in a position)
        uint256 volume = pos.isLong
            ? _registerVolumeBid(
                data,
                pos.oiCurrent(fraction, totalOi, totalOiShares),
                capOiAdjustedForBounds(data, capOi)
            )
            : _registerVolumeAsk(
                data,
                pos.oiCurrent(fraction, totalOi, totalOiShares),
                capOiAdjustedForBounds(data, capOi)
            );
        uint256 price = pos.isLong ? bid(data, volume) : ask(data, volume);
        // check price hasn't changed more than max slippage specified by trader
        require(pos.isLong ? price >= priceLimit : price <= priceLimit, "OVLV1:slippage>max");

        // calculate the value and cost of the position for pnl determinations
        // and amount to transfer
        uint256 value = pos.value(fraction, totalOi, totalOiShares, price, capPayoff);
        uint256 cost = pos.cost(fraction);

        // register the amount to be minted/burned
        // capPayoff prevents overflow reverts with int256 cast
        _registerMint(int256(value) - int256(cost));

        // calculate the trading fee as % on notional
        uint256 tradingFee = pos.tradingFee(
            fraction,
            totalOi,
            totalOiShares,
            price,
            capPayoff,
            tradingFeeRate
        );
        // TODO: move this min to position lib
        tradingFee = Math.min(tradingFee, value); // if value < tradingFee

        // subtract unwound open interest from the side's aggregate oi value
        // and decrease number of oi shares issued
        if (pos.isLong) {
            oiLong -= pos.oiCurrent(fraction, totalOi, totalOiShares);
            oiLongShares -= pos.oiSharesCurrent(fraction);
        } else {
            oiShort -= pos.oiCurrent(fraction, totalOi, totalOiShares);
            oiShortShares -= pos.oiSharesCurrent(fraction);
        }

        // store the updated position info data
        pos.oiShares -= uint120(pos.oiSharesCurrent(fraction));
        pos.debt -= uint120(pos.debtCurrent(fraction));
        positions.set(msg.sender, positionId, pos);

        // emit unwind event
        emit Unwind(msg.sender, positionId, fraction, int256(value) - int256(cost), price);

        // mint or burn the pnl for the position
        if (value >= cost) {
            ovl.mint(address(this), value - cost);
        } else {
            ovl.burn(cost - value);
        }

        // transfer out the unwound position value less fees to trader
        ovl.transfer(msg.sender, value - tradingFee);

        // send trading fees to trading fee recipient
        ovl.transfer(tradingFeeRecipient, tradingFee);
    }

    /// @dev liquidates a liquidatable position
    function liquidate(address owner, uint256 positionId) external {
        // check position exists
        Position.Info memory pos = positions.get(owner, positionId);
        require(pos.exists(), "OVLV1:!position");

        // call to update before any effects
        Oracle.Data memory data = update();

        // cache for gas savings
        uint256 totalOi = pos.isLong ? oiLong : oiShort;
        uint256 totalOiShares = pos.isLong ? oiLongShares : oiShortShares;
        uint256 _capPayoff = capPayoff;

        // entire position should be liquidated
        uint256 fraction = ONE;

        // longs get the bid and shorts get the ask on liquidate
        // NOTE: liquidated position's oi should *not* add additional volume to roller
        // NOTE: since market impact intended to mitigate front-running (not relevant here)
        uint256 volume = pos.isLong
            ? _registerVolumeBid(data, 0, capOi)
            : _registerVolumeAsk(data, 0, capOi);
        uint256 price = pos.isLong ? bid(data, volume) : ask(data, volume);

        // check position is liquidatable
        // TODO: rename maintenanceMargin storage var => maintenanceMarginFraction
        // TODO: to avoid confusion w actual maintenance margin
        // TODO: rename isLiquidatable => liquidatable
        require(
            pos.isLiquidatable(totalOi, totalOiShares, price, _capPayoff, maintenanceMargin),
            "OVLV1:!liquidatable"
        );

        // calculate the value and cost of the position for pnl determinations
        // and amount to transfer
        uint256 value = pos.value(fraction, totalOi, totalOiShares, price, _capPayoff);
        uint256 cost = pos.cost(fraction);

        // value is the remaining position margin. reduce value further by
        // the mm burn rate, as insurance for cases when not liquidated in time
        value -= value.mulUp(maintenanceMarginBurnRate);

        // register the amount to be burned
        _registerMint(int256(value) - int256(cost));

        // TODO: calculate the liquidation fee as % on remaining value
        // TODO: liquidationFee = pos.liquidationFee()
        uint256 liquidationFee = 0;

        // subtract liquidated open interest from the side's aggregate oi value
        // and decrease number of oi shares issued
        if (pos.isLong) {
            oiLong -= pos.oiCurrent(fraction, totalOi, totalOiShares);
            oiLongShares -= pos.oiSharesCurrent(fraction);
        } else {
            oiShort -= pos.oiCurrent(fraction, totalOi, totalOiShares);
            oiShortShares -= pos.oiSharesCurrent(fraction);
        }

        // store the updated position info data. mark as liquidated
        pos.oiShares = 0;
        pos.debt = 0;
        pos.liquidated = true;
        positions.set(owner, positionId, pos);

        // emit liquidate event
        emit Liquidate(msg.sender, owner, positionId, int256(value) - int256(cost), price);

        // burn the pnl for the position
        ovl.burn(cost - value);

        // transfer out the remaining position value less fees to liquidator for reward
        ovl.transfer(msg.sender, value - liquidationFee);

        // send liquidation fees to trading fee recipient
        // TODO: rename tradingFeeRecipient to feeRecipient
        ovl.transfer(tradingFeeRecipient, liquidationFee);
    }

    /// @dev updates market: pays funding and fetches freshest data from feed
    /// @dev update is called every time market is interacted with
    function update() public returns (Oracle.Data memory) {
        // apply funding if at least one block has passed
        uint256 timeElapsed = block.timestamp - timestampUpdateLast;
        if (timeElapsed > 0) {
            // calculate adjustments to oi due to funding
            bool isLongOverweight = oiLong > oiShort;
            uint256 oiOverweight = isLongOverweight ? oiLong : oiShort;
            uint256 oiUnderweight = isLongOverweight ? oiShort : oiLong;
            (oiOverweight, oiUnderweight) = oiAfterFunding(
                oiOverweight,
                oiUnderweight,
                timeElapsed
            );

            // pay funding
            oiLong = isLongOverweight ? oiOverweight : oiUnderweight;
            oiShort = isLongOverweight ? oiUnderweight : oiOverweight;

            // refresh last update data
            timestampUpdateLast = block.timestamp;
        }

        // fetch new oracle data from feed
        // applies sanity check in case of data manipulation
        Oracle.Data memory data = IOverlayV1Feed(feed).latest();
        require(dataIsValid(data), "OVLV1:!data");

        // return the latest data from feed
        return data;
    }

    /// @dev sanity check on data fetched from oracle in case of manipulation
    /// @dev rough check that log price bounded by +/- priceDriftUpperLimit * dt
    /// @dev when comparing priceMacro(now) vs priceMacro(now - macroWindow)
    function dataIsValid(Oracle.Data memory data) public view returns (bool) {
        // upper and lower limits are e**(+/- priceDriftUpperLimit * dt)
        uint256 pow = priceDriftUpperLimit * data.macroWindow;
        uint256 dpLowerLimit = INVERSE_EULER.powUp(pow);
        uint256 dpUpperLimit = EULER.powUp(pow);

        // compare current price over macro window vs price over macro window
        // one macro window in the past
        uint256 priceNow = data.priceOverMacroWindow;
        uint256 priceLast = data.priceOneMacroWindowAgo;
        if (priceLast == 0 || priceNow == 0) {
            // data is not valid if price is zero
            return false;
        }

        // price is valid if within upper and lower limits on drift given
        // time elapsed over one macro window
        uint256 dp = priceNow.divUp(priceLast);
        return (dp >= dpLowerLimit && dp <= dpUpperLimit);
    }

    /// @dev current open interest after funding payments transferred
    /// @dev from overweight oi side to underweight oi side
    function oiAfterFunding(
        uint256 oiOverweight,
        uint256 oiUnderweight,
        uint256 timeElapsed
    ) public view returns (uint256, uint256) {
        uint256 oiTotal = oiOverweight + oiUnderweight;

        // draw down the imbalance by factor of (1-2k)^(t)
        uint256 drawdownFactor = (ONE - 2 * k).powUp(ONE * timeElapsed);
        uint256 oiImbalanceNow = drawdownFactor.mulUp(oiOverweight - oiUnderweight);

        if (oiUnderweight == 0) {
            // user pays the protocol thru burn if one side has zero oi
            oiOverweight = oiImbalanceNow;
        } else {
            // overweight pays underweight side if oi on both sides
            oiOverweight = (oiTotal + oiImbalanceNow) / 2;
            oiUnderweight = (oiTotal - oiImbalanceNow) / 2;
        }
        return (oiOverweight, oiUnderweight);
    }

    /// @return next position id
    function nextPositionId() external view returns (uint256) {
        return _totalPositions;
    }

    /// @dev current open interest cap with adjustments to lower open
    /// @dev interest cap in event market has printed a lot in recent past
    function capOiAdjustedForCircuitBreaker(uint256 cap) public view returns (uint256) {
        // Adjust cap downward for circuit breaker. Use snapshotMinted
        // but transformed to account for decay in magnitude of minted since
        // last snapshot taken
        Roller.Snapshot memory snapshot = snapshotMinted;
        snapshot = snapshot.transform(block.timestamp, circuitBreakerWindow, 0);
        cap = Math.min(cap, circuitBreaker(snapshot, cap));
        return cap;
    }

    /// @dev bound on open interest cap from circuit breaker
    /// @dev Three cases:
    /// @dev 1. minted < 1x target amount over circuitBreakerWindow: return capOi
    /// @dev 2. minted > 2x target amount over last circuitBreakerWindow: return 0
    /// @dev 3. minted between 1x and 2x target amount: return capOi * (2 - minted/target)
    function circuitBreaker(Roller.Snapshot memory snapshot, uint256 cap)
        public
        view
        returns (uint256)
    {
        int256 minted = int256(snapshot.cumulative());
        uint256 _circuitBreakerMintTarget = circuitBreakerMintTarget;
        if (minted <= int256(_circuitBreakerMintTarget)) {
            return cap;
        } else if (minted >= 2 * int256(_circuitBreakerMintTarget)) {
            return 0;
        }

        // case 3 (circuit breaker adjustment downward)
        uint256 adjustment = (2 * ONE).sub(uint256(minted).divDown(_circuitBreakerMintTarget));
        return cap.mulDown(adjustment);
    }

    /// @dev current open interest cap with adjustments to prevent
    /// @dev front-running trade and back-running trade
    function capOiAdjustedForBounds(Oracle.Data memory data, uint256 cap)
        public
        view
        returns (uint256)
    {
        if (data.hasReserve) {
            // Adjust cap downward if exceeds bounds from front run attack
            cap = Math.min(cap, frontRunBound(data));

            // Adjust cap downward if exceeds bounds from back run attack
            cap = Math.min(cap, backRunBound(data));
        }
        return cap;
    }

    /// @dev bound on open interest cap to mitigate front-running attack
    /// @dev bound = lmbda * reserveInOvl / 2
    function frontRunBound(Oracle.Data memory data) public view returns (uint256) {
        return lmbda.mulDown(data.reserveOverMicroWindow).divDown(2 * ONE);
    }

    /// @dev bound on open interest cap to mitigate back-running attack
    /// @dev bound = macroWindow * reserveInOvl * 2 * delta
    function backRunBound(Oracle.Data memory data) public view returns (uint256) {
        // TODO: macroWindow should be in blocks in current spec. What to do here to be
        // futureproof vs having an average block time constant (BAD)
        uint256 window = (data.macroWindow * ONE) / AVERAGE_BLOCK_TIME;
        return delta.mulDown(data.reserveOverMicroWindow).mulDown(window).mulDown(2 * ONE);
    }

    /// @dev bid price given oracle data and recent volume
    function bid(Oracle.Data memory data, uint256 volume) public view returns (uint256 bid_) {
        bid_ = Math.min(data.priceOverMicroWindow, data.priceOverMacroWindow);

        // add static spread (delta) and market impact (lmbda * volume)
        uint256 pow = delta + lmbda.mulUp(volume);
        require(pow <= MAX_NATURAL_EXPONENT, "OVLV1:slippage>max");

        bid_ = bid_.mulDown(INVERSE_EULER.powUp(pow));
    }

    /// @dev ask price given oracle data and recent volume
    function ask(Oracle.Data memory data, uint256 volume) public view returns (uint256 ask_) {
        ask_ = Math.max(data.priceOverMicroWindow, data.priceOverMacroWindow);

        // add static spread (delta) and market impact (lmbda * volume)
        uint256 pow = delta + lmbda.mulUp(volume);
        require(pow <= MAX_NATURAL_EXPONENT, "OVLV1:slippage>max");

        ask_ = ask_.mulUp(EULER.powUp(pow));
    }

    /// @dev mid price given oracle data and recent volume
    function mid(
        Oracle.Data memory data,
        uint256 volumeBid,
        uint256 volumeAsk
    ) public view returns (uint256 mid_) {
        mid_ = (bid(data, volumeBid) + ask(data, volumeAsk)) / 2;
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
        uint256 volume = uint256(snapshot.cumulative());
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
        uint256 volume = uint256(snapshot.cumulative());
        return volume;
    }

    /// @dev Rolling mint accumulator to be used for circuit breaker
    function _registerMint(int256 value) private returns (int256) {
        // save gas with snapshot in memory
        Roller.Snapshot memory snapshot = snapshotMinted;

        // calculates the decay in the rolling amount minted since last snapshot
        // and determines new window to decay over
        snapshot = snapshot.transform(block.timestamp, circuitBreakerWindow, value);

        // store the transformed snapshot
        snapshotMinted = snapshot;

        // return the cumulative mint amount
        int256 minted = snapshot.cumulative();
        return minted;
    }

    /// TODO: emergencyWithdraw(?): allows withdrawal of original collateral
    /// TODO: without profit/loss if system in emergencyShutdown mode

    /// @dev governance adjustable risk parameter setters
    /// @dev min/max bounds checks to risk params imposed at factory level
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

    function setCircuitBreakerWindow(uint256 _circuitBreakerWindow) external onlyFactory {
        circuitBreakerWindow = _circuitBreakerWindow;
    }

    function setCircuitBreakerMintTarget(uint256 _circuitBreakerMintTarget) external onlyFactory {
        circuitBreakerMintTarget = _circuitBreakerMintTarget;
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

    function setPriceDriftUpperLimit(uint256 _priceDriftUpperLimit) external onlyFactory {
        // TODO: check pow != 0 && pow <= MAX_NATURAL_EXPONENT; pow = drift * data.macroWindow
        priceDriftUpperLimit = _priceDriftUpperLimit;
    }
}
