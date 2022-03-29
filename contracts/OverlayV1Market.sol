// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/Math.sol";

import "./interfaces/IOverlayV1Factory.sol";
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
    using Risk for uint256[14];
    using Roller for Roller.Snapshot;

    // internal constants
    uint256 internal constant ONE = 1e18; // 18 decimal places
    uint256 internal constant AVERAGE_BLOCK_TIME = 14; // (BAD) TODO: remove since not futureproof

    // cap for euler exponent powers; SEE: ./libraries/LogExpMath.sol::pow
    // using ~ 1/2 library max for substantial padding
    uint256 internal constant MAX_NATURAL_EXPONENT = 20e18;
    uint256 internal constant EULER = 2718281828459045091; // 2.71828e18
    uint256 internal constant INVERSE_EULER = 367879441171442334; // 0.367879e18

    // immutables
    IOverlayV1Token public immutable ovl; // ovl token
    address public immutable feed; // oracle feed
    address public immutable factory; // factory that deployed this market

    // risk params
    uint256[14] public params; // params.idx order based on Risk.Parameters enum

    // aggregate oi quantities
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

    // cached risk calcs
    uint256 public dpUpperLimit; // e**(+priceDriftUpperLimit * macroWindow)

    // factory modifier for governance sensitive functions
    modifier onlyFactory() {
        require(msg.sender == factory, "OVLV1: !factory");
        _;
    }

    // events for core functions
    event Build(
        address indexed sender, // address that initiated build (owns position)
        uint256 positionId, // id of built position
        uint256 oi, // oi of position at build
        uint256 debt, // debt of position at build
        bool isLong, // whether is long or short
        uint256 price // entry price
    );
    event Unwind(
        address indexed sender, // address that initiated unwind (owns position)
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
        uint256[14] memory _params
    ) {
        ovl = IOverlayV1Token(_ovl);
        feed = _feed;
        factory = _factory;

        // initialize update data
        Oracle.Data memory data = IOverlayV1Feed(feed).latest();
        require(_midFromFeed(data) > 0, "OVLV1:!data");
        timestampUpdateLast = block.timestamp;

        // check risk params valid
        uint256 _capLeverage = _params[uint256(Risk.Parameters.CapLeverage)];
        uint256 _delta = _params[uint256(Risk.Parameters.Delta)];
        uint256 _maintenanceMarginFraction = _params[
            uint256(Risk.Parameters.MaintenanceMarginFraction)
        ];
        require(
            _capLeverage <= ONE.divDown(2 * _delta + _maintenanceMarginFraction),
            "OVLV1: max lev immediately liquidatable"
        );

        uint256 _priceDriftUpperLimit = _params[uint256(Risk.Parameters.PriceDriftUpperLimit)];
        require(
            _priceDriftUpperLimit * data.macroWindow < MAX_NATURAL_EXPONENT,
            "OVLV1: price drift exceeds max exp"
        );
        _cacheRiskCalc(Risk.Parameters.PriceDriftUpperLimit, _priceDriftUpperLimit);

        // set the risk params
        for (uint256 i = 0; i < _params.length; i++) {
            params[i] = _params[i];
        }
    }

    /// @dev builds a new position
    function build(
        uint256 collateral,
        uint256 leverage,
        bool isLong,
        uint256 priceLimit
    ) external returns (uint256 positionId_) {
        require(leverage >= ONE, "OVLV1:lev<min");
        require(leverage <= params.get(Risk.Parameters.CapLeverage), "OVLV1:lev>max");
        require(collateral >= params.get(Risk.Parameters.MinCollateral), "OVLV1:collateral<min");

        uint256 oi;
        uint256 debt;
        uint256 price;
        uint256 tradingFee;
        // avoids stack too deep
        {
            // call to update before any effects
            Oracle.Data memory data = update();

            // calculate notional, oi, and trading fees. fees charged on notional
            // and added to collateral transferred in
            uint256 notional = collateral.mulUp(leverage);
            oi = oiFromNotional(data, notional);
            debt = notional - collateral;
            tradingFee = notional.mulUp(params.get(Risk.Parameters.TradingFeeRate));

            // calculate current notional cap adjusted for circuit breaker *then* adjust
            // for front run and back run bounds (order matters)
            // finally, transform into a cap on open interest
            uint256 capNotionalAdjusted = capNotionalAdjustedForBounds(
                data,
                capNotionalAdjustedForCircuitBreaker(params.get(Risk.Parameters.CapNotional))
            );
            uint256 capOi = oiFromNotional(data, capNotionalAdjusted);

            // longs get the ask and shorts get the bid on build
            // register the additional volume on either the ask or bid
            // where volume = oi / capOi
            price = isLong
                ? ask(data, _registerVolumeAsk(data, oi, capOi))
                : bid(data, _registerVolumeBid(data, oi, capOi));
            // check price hasn't changed more than max slippage specified by trader
            require(isLong ? price <= priceLimit : price >= priceLimit, "OVLV1:slippage>max");

            // add new position's open interest to the side's aggregate oi value
            // and increase number of oi shares issued. assemble position for storage

            // cache for gas savings
            uint256 oiTotalOnSide = isLong ? oiLong : oiShort;
            uint256 oiTotalSharesOnSide = isLong ? oiLongShares : oiShortShares;

            // check new total oi on side does not exceed capOi
            oiTotalOnSide += oi;
            oiTotalSharesOnSide += oi;
            require(oiTotalOnSide <= capOi, "OVLV1:oi>cap");

            // update total aggregate oi and oi shares
            if (isLong) {
                oiLong = oiTotalOnSide;
                oiLongShares = oiTotalSharesOnSide;
            } else {
                oiShort = oiTotalOnSide;
                oiShortShares = oiTotalSharesOnSide;
            }

            // assemble position info data
            // check position is not immediately liquidatable prior to storing
            Position.Info memory pos = Position.Info({
                notional: uint120(notional), // won't overflow as capNotional max is 8e24
                debt: uint120(debt),
                isLong: isLong,
                liquidated: false,
                entryPrice: price,
                oiShares: oi
            });
            require(
                !pos.liquidatable(
                    oiTotalOnSide,
                    oiTotalSharesOnSide,
                    _midFromFeed(data), // mid price used on liquidations
                    params.get(Risk.Parameters.CapPayoff),
                    params.get(Risk.Parameters.MaintenanceMarginFraction)
                ),
                "OVLV1:liquidatable"
            );

            // store the position info data
            positionId_ = _totalPositions;
            positions.set(msg.sender, positionId_, pos);
            _totalPositions++;
        }

        // emit build event
        emit Build(msg.sender, positionId_, oi, debt, isLong, price);

        // transfer in the OVL collateral needed to back the position + fees
        // trading fees charged as a percentage on notional size of position
        ovl.transferFrom(msg.sender, address(this), collateral + tradingFee);

        // send trading fees to trading fee recipient
        ovl.transfer(IOverlayV1Factory(factory).feeRecipient(), tradingFee);
    }

    /// @dev unwinds fraction of an existing position
    function unwind(
        uint256 positionId,
        uint256 fraction,
        uint256 priceLimit
    ) external {
        require(fraction > 0, "OVLV1:fraction<min");
        require(fraction <= ONE, "OVLV1:fraction>max");

        uint256 value;
        uint256 cost;
        uint256 price;
        uint256 tradingFee;
        // avoids stack too deep
        {
            // call to update before any effects
            Oracle.Data memory data = update();

            // check position exists
            Position.Info memory pos = positions.get(msg.sender, positionId);
            require(pos.exists(), "OVLV1:!position");

            // cache for gas savings
            uint256 oiTotalOnSide = pos.isLong ? oiLong : oiShort;
            uint256 oiTotalSharesOnSide = pos.isLong ? oiLongShares : oiShortShares;

            // longs get the bid and shorts get the ask on unwind
            // register the additional volume on either the ask or bid
            // where volume = oi / capOi
            // current cap only adjusted for bounds (no circuit breaker so traders
            // don't get stuck in a position)
            uint256 capOi = oiFromNotional(
                data,
                capNotionalAdjustedForBounds(data, params.get(Risk.Parameters.CapNotional))
            );
            price = pos.isLong
                ? bid(
                    data,
                    _registerVolumeBid(
                        data,
                        pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide),
                        capOi
                    )
                )
                : ask(
                    data,
                    _registerVolumeAsk(
                        data,
                        pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide),
                        capOi
                    )
                );
            // check price hasn't changed more than max slippage specified by trader
            require(pos.isLong ? price >= priceLimit : price <= priceLimit, "OVLV1:slippage>max");

            // calculate the value and cost of the position for pnl determinations
            // and amount to transfer
            uint256 capPayoff = params.get(Risk.Parameters.CapPayoff);
            value = pos.value(fraction, oiTotalOnSide, oiTotalSharesOnSide, price, capPayoff);
            cost = pos.cost(fraction);

            // calculate the trading fee as % on notional
            uint256 tradingFeeRate = params.get(Risk.Parameters.TradingFeeRate);
            tradingFee = pos.tradingFee(
                fraction,
                oiTotalOnSide,
                oiTotalSharesOnSide,
                price,
                capPayoff,
                tradingFeeRate
            );
            tradingFee = Math.min(tradingFee, value); // if value < tradingFee

            // subtract unwound open interest from the side's aggregate oi value
            // and decrease number of oi shares issued
            // use subFloor to avoid reverts with rounding issues
            if (pos.isLong) {
                oiLong = oiLong.subFloor(pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide));
                oiLongShares = oiLongShares.subFloor(pos.oiSharesCurrent(fraction));
            } else {
                oiShort = oiShort.subFloor(pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide));
                oiShortShares = oiShortShares.subFloor(pos.oiSharesCurrent(fraction));
            }

            // register the amount to be minted/burned
            // capPayoff prevents overflow reverts with int256 cast
            _registerMintOrBurn(int256(value) - int256(cost));

            // store the updated position info data
            // use subFloor to avoid reverts with rounding issues
            pos.notional = uint120(uint256(pos.notional).subFloor(pos.notionalInitial(fraction)));
            pos.debt = uint120(uint256(pos.debt).subFloor(pos.debtCurrent(fraction)));
            pos.oiShares = pos.oiShares.subFloor(pos.oiSharesCurrent(fraction));
            positions.set(msg.sender, positionId, pos);
        }

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
        ovl.transfer(IOverlayV1Factory(factory).feeRecipient(), tradingFee);
    }

    /// @dev liquidates a liquidatable position
    function liquidate(address owner, uint256 positionId) external {
        // check position exists
        Position.Info memory pos = positions.get(owner, positionId);
        require(pos.exists(), "OVLV1:!position");

        // call to update before any effects
        Oracle.Data memory data = update();

        // cache for gas savings
        uint256 oiTotalOnSide = pos.isLong ? oiLong : oiShort;
        uint256 oiTotalSharesOnSide = pos.isLong ? oiLongShares : oiShortShares;
        uint256 capPayoff = params.get(Risk.Parameters.CapPayoff);

        // entire position should be liquidated
        uint256 fraction = ONE;

        // Use mid price without volume for liquidation (oracle price effectively) to
        // prevent market impact manipulation from causing unneccessary liquidations
        uint256 price = _midFromFeed(data);

        // check position is liquidatable
        require(
            pos.liquidatable(
                oiTotalOnSide,
                oiTotalSharesOnSide,
                price,
                capPayoff,
                params.get(Risk.Parameters.MaintenanceMarginFraction)
            ),
            "OVLV1:!liquidatable"
        );

        // calculate the value and cost of the position for pnl determinations
        // and amount to transfer
        uint256 value = pos.value(fraction, oiTotalOnSide, oiTotalSharesOnSide, price, capPayoff);
        uint256 cost = pos.cost(fraction);

        // value is the remaining position margin. reduce value further by
        // the mm burn rate, as insurance for cases when not liquidated in time
        value -= value.mulDown(params.get(Risk.Parameters.MaintenanceMarginBurnRate));

        // calculate the liquidation fee as % on remaining value
        uint256 liquidationFee = value.mulDown(params.get(Risk.Parameters.LiquidationFeeRate));

        // subtract liquidated open interest from the side's aggregate oi value
        // and decrease number of oi shares issued
        // use subFloor to avoid reverts with rounding issues
        if (pos.isLong) {
            oiLong = oiLong.subFloor(pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide));
            oiLongShares = oiLongShares.subFloor(pos.oiSharesCurrent(fraction));
        } else {
            oiShort = oiShort.subFloor(pos.oiCurrent(fraction, oiTotalOnSide, oiTotalSharesOnSide));
            oiShortShares = oiShortShares.subFloor(pos.oiSharesCurrent(fraction));
        }

        // register the amount to be burned
        _registerMintOrBurn(int256(value) - int256(cost));

        // store the updated position info data. mark as liquidated
        pos.notional = 0;
        pos.debt = 0;
        pos.oiShares = 0;
        pos.liquidated = true;
        pos.entryPrice = 0;
        positions.set(owner, positionId, pos);

        // emit liquidate event
        emit Liquidate(msg.sender, owner, positionId, int256(value) - int256(cost), price);

        // burn the pnl for the position
        ovl.burn(cost - value);

        // transfer out the remaining position value less fees to liquidator for reward
        ovl.transfer(msg.sender, value - liquidationFee);

        // send liquidation fees to trading fee recipient
        ovl.transfer(IOverlayV1Factory(factory).feeRecipient(), liquidationFee);
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
        uint256 _dpUpperLimit = dpUpperLimit;
        uint256 _dpLowerLimit = ONE.divDown(_dpUpperLimit);

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
        return (dp >= _dpLowerLimit && dp <= _dpUpperLimit);
    }

    /// @notice Current open interest after funding payments transferred
    /// @notice from overweight oi side to underweight oi side
    /// @dev The value of oiOverweight must be >= oiUnderweight
    function oiAfterFunding(
        uint256 oiOverweight,
        uint256 oiUnderweight,
        uint256 timeElapsed
    ) public view returns (uint256, uint256) {
        uint256 oiTotal = oiOverweight + oiUnderweight;
        uint256 oiImbalance = oiOverweight - oiUnderweight;
        uint256 oiInvariant = oiUnderweight.mulUp(oiOverweight);

        // If no OI or imbalance, no funding occurs. Handles div by zero case below
        if (oiTotal == 0 || oiImbalance == 0) {
            return (oiOverweight, oiUnderweight);
        }

        // draw down the imbalance by factor of e**(-2*k*t)
        // but min to zero if pow = 2*k*t exceeds MAX_NATURAL_EXPONENT
        uint256 fundingFactor;
        uint256 pow = 2 * params.get(Risk.Parameters.K) * timeElapsed;
        if (pow < MAX_NATURAL_EXPONENT) {
            fundingFactor = INVERSE_EULER.powDown(pow);
        }

        // Decrease total aggregate open interest (i.e. oiLong + oiShort)
        // to compensate protocol for pro-rata share of imbalance liability
        // OI_tot(t) = OI_tot(0) * \
        //  sqrt( 1 - (OI_imb(0)/OI_tot(0))**2 * (1 - e**(-4*k*t)) )

        // Guaranteed 0 <= underRoot <= 1
        uint256 underRoot = ONE -
            oiImbalance.divDown(oiTotal).mulDown(oiImbalance.divDown(oiTotal)).mulDown(
                ONE - fundingFactor.mulDown(fundingFactor)
            );

        // oiTotalNow guaranteed <= oiTotalBefore (burn happens)
        oiTotal = oiTotal.mulDown(underRoot.powDown(ONE / 2));

        // Time decay imbalance: OI_imb(t) = OI_imb(0) * e**(-2*k*t)
        // oiImbalanceNow guaranteed <= oiImbalanceBefore
        oiImbalance = oiImbalance.mulDown(fundingFactor);

        // overweight pays underweight
        // use oiOver * oiUnder = invariant for oiUnderNow to avoid any
        // potential overflow reverts
        oiOverweight = (oiTotal + oiImbalance) / 2;
        if (oiOverweight != 0) {
            oiUnderweight = oiInvariant.divUp(oiOverweight);
        }
        return (oiOverweight, oiUnderweight);
    }

    /// @dev current notional cap with adjustments to lower
    /// @dev cap in the event market has printed a lot in recent past
    function capNotionalAdjustedForCircuitBreaker(uint256 cap) public view returns (uint256) {
        // Adjust cap downward for circuit breaker. Use snapshotMinted
        // but transformed to account for decay in magnitude of minted since
        // last snapshot taken
        Roller.Snapshot memory snapshot = snapshotMinted;
        uint256 circuitBreakerWindow = params.get(Risk.Parameters.CircuitBreakerWindow);
        snapshot = snapshot.transform(block.timestamp, circuitBreakerWindow, 0);
        cap = circuitBreaker(snapshot, cap);
        return cap;
    }

    /// @dev bound on notional cap from circuit breaker
    /// @dev Three cases:
    /// @dev 1. minted < 1x target amount over circuitBreakerWindow: return cap
    /// @dev 2. minted > 2x target amount over last circuitBreakerWindow: return 0
    /// @dev 3. minted between 1x and 2x target amount: return cap * (2 - minted/target)
    function circuitBreaker(Roller.Snapshot memory snapshot, uint256 cap)
        public
        view
        returns (uint256)
    {
        int256 minted = int256(snapshot.cumulative());
        uint256 circuitBreakerMintTarget = params.get(Risk.Parameters.CircuitBreakerMintTarget);
        if (minted <= int256(circuitBreakerMintTarget)) {
            return cap;
        } else if (minted >= 2 * int256(circuitBreakerMintTarget)) {
            return 0;
        }

        // case 3 (circuit breaker adjustment downward)
        uint256 adjustment = 2 * ONE - uint256(minted).divDown(circuitBreakerMintTarget);
        return cap.mulDown(adjustment);
    }

    /// @dev current notional cap with adjustments to prevent
    /// @dev front-running trade and back-running trade
    function capNotionalAdjustedForBounds(Oracle.Data memory data, uint256 cap)
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

    /// @dev bound on notional cap to mitigate front-running attack
    /// @dev bound = lmbda * reserveInOvl
    function frontRunBound(Oracle.Data memory data) public view returns (uint256) {
        uint256 lmbda = params.get(Risk.Parameters.Lmbda);
        return lmbda.mulDown(data.reserveOverMicroWindow);
    }

    /// @dev bound on notional cap to mitigate back-running attack
    /// @dev bound = macroWindowInBlocks * reserveInOvl * 2 * delta
    function backRunBound(Oracle.Data memory data) public view returns (uint256) {
        // TODO: macroWindow should be in blocks in current spec. What to do here to be
        // futureproof vs having an average block time constant (BAD)
        uint256 window = (data.macroWindow * ONE) / AVERAGE_BLOCK_TIME;
        uint256 delta = params.get(Risk.Parameters.Delta);
        return delta.mulDown(data.reserveOverMicroWindow).mulDown(window).mulDown(2 * ONE);
    }

    /// @dev Returns the open interest in number of contracts for a given notional
    /// @dev Uses _midFromFeed(data) price to calculate oi: OI = Q / P
    // TODO: fix potential rounding errors w div and large prices; move to Position lib
    function oiFromNotional(Oracle.Data memory data, uint256 notional)
        public
        view
        returns (uint256)
    {
        uint256 price = _midFromFeed(data);
        return notional.divDown(price);
    }

    /// @dev bid price given oracle data and recent volume
    function bid(Oracle.Data memory data, uint256 volume) public view returns (uint256 bid_) {
        bid_ = Math.min(data.priceOverMicroWindow, data.priceOverMacroWindow);

        // add static spread (delta) and market impact (lmbda * volume)
        uint256 delta = params.get(Risk.Parameters.Delta);
        uint256 lmbda = params.get(Risk.Parameters.Lmbda);
        uint256 pow = delta + lmbda.mulUp(volume);
        require(pow < MAX_NATURAL_EXPONENT, "OVLV1:slippage>max");

        bid_ = bid_.mulDown(INVERSE_EULER.powUp(pow));
    }

    /// @dev ask price given oracle data and recent volume
    function ask(Oracle.Data memory data, uint256 volume) public view returns (uint256 ask_) {
        ask_ = Math.max(data.priceOverMicroWindow, data.priceOverMacroWindow);

        // add static spread (delta) and market impact (lmbda * volume)
        uint256 delta = params.get(Risk.Parameters.Delta);
        uint256 lmbda = params.get(Risk.Parameters.Lmbda);
        uint256 pow = delta + lmbda.mulUp(volume);
        require(pow < MAX_NATURAL_EXPONENT, "OVLV1:slippage>max");

        ask_ = ask_.mulUp(EULER.powUp(pow));
    }

    /// @dev mid price without impact/spread given oracle data and recent volume
    /// @dev used for gas savings to avoid accessing storage for delta, lmbda
    function _midFromFeed(Oracle.Data memory data) private view returns (uint256 mid_) {
        mid_ = Math.average(data.priceOverMicroWindow, data.priceOverMacroWindow);
    }

    /// @dev Rolling volume adjustments on bid side to be used for market impact.
    /// @dev Volume values are normalized with respect to cap
    function _registerVolumeBid(
        Oracle.Data memory data,
        uint256 volume,
        uint256 cap
    ) private returns (uint256) {
        // save gas with snapshot in memory
        Roller.Snapshot memory snapshot = snapshotVolumeBid;
        int256 value = int256(volume.divUp(cap));

        // calculates the decay in the rolling volume since last snapshot
        // and determines new window to decay over
        snapshot = snapshot.transform(block.timestamp, data.microWindow, value);

        // store the transformed snapshot
        snapshotVolumeBid = snapshot;

        // return the cumulative volume
        return uint256(snapshot.cumulative());
    }

    /// @dev Rolling volume adjustments on ask side to be used for market impact.
    /// @dev Volume values are normalized with respect to cap
    function _registerVolumeAsk(
        Oracle.Data memory data,
        uint256 volume,
        uint256 cap
    ) private returns (uint256) {
        // save gas with snapshot in memory
        Roller.Snapshot memory snapshot = snapshotVolumeAsk;
        int256 value = int256(volume.divUp(cap));

        // calculates the decay in the rolling volume since last snapshot
        // and determines new window to decay over
        snapshot = snapshot.transform(block.timestamp, data.microWindow, value);

        // store the transformed snapshot
        snapshotVolumeAsk = snapshot;

        // return the cumulative volume
        return uint256(snapshot.cumulative());
    }

    /// @notice Rolling mint accumulator to be used for circuit breaker
    /// @dev value > 0 registers a mint, value <= 0 registers a burn
    function _registerMintOrBurn(int256 value) private returns (int256) {
        // save gas with snapshot in memory
        Roller.Snapshot memory snapshot = snapshotMinted;

        // calculates the decay in the rolling amount minted since last snapshot
        // and determines new window to decay over
        uint256 circuitBreakerWindow = params.get(Risk.Parameters.CircuitBreakerWindow);
        snapshot = snapshot.transform(block.timestamp, circuitBreakerWindow, value);

        // store the transformed snapshot
        snapshotMinted = snapshot;

        // return the cumulative mint amount
        int256 minted = snapshot.cumulative();
        return minted;
    }

    /// @notice Sets the governance per-market risk parameter
    function setRiskParam(Risk.Parameters name, uint256 value) external onlyFactory {
        _checkRiskParam(name, value);
        _cacheRiskCalc(name, value);
        params.set(name, value);
    }

    /// @notice Checks the governance per-market risk parameter is valid
    function _checkRiskParam(Risk.Parameters name, uint256 value) private {
        // checks delta won't cause position to be immediately
        // liquidatable given current leverage cap (capLeverage) and
        // maintenance margin fraction (maintenanceMarginFraction)
        if (name == Risk.Parameters.Delta) {
            uint256 _delta = value;
            uint256 capLeverage = params.get(Risk.Parameters.CapLeverage);
            uint256 maintenanceMarginFraction = params.get(
                Risk.Parameters.MaintenanceMarginFraction
            );
            require(
                capLeverage <= ONE.divDown(2 * _delta + maintenanceMarginFraction),
                "OVLV1: max lev immediately liquidatable"
            );
        }

        // checks capLeverage won't cause position to be immediately
        // liquidatable given current spread (delta) and
        // maintenance margin fraction (maintenanceMarginFraction)
        if (name == Risk.Parameters.CapLeverage) {
            uint256 _capLeverage = value;
            uint256 delta = params.get(Risk.Parameters.Delta);
            uint256 maintenanceMarginFraction = params.get(
                Risk.Parameters.MaintenanceMarginFraction
            );
            require(
                _capLeverage <= ONE.divDown(2 * delta + maintenanceMarginFraction),
                "OVLV1: max lev immediately liquidatable"
            );
        }

        // checks maintenanceMarginFraction won't cause position
        // to be immediately liquidatable given current spread (delta)
        // and leverage cap (capLeverage)
        if (name == Risk.Parameters.MaintenanceMarginFraction) {
            uint256 _maintenanceMarginFraction = value;
            uint256 delta = params.get(Risk.Parameters.Delta);
            uint256 capLeverage = params.get(Risk.Parameters.CapLeverage);
            require(
                capLeverage <= ONE.divDown(2 * delta + _maintenanceMarginFraction),
                "OVLV1: max lev immediately liquidatable"
            );
        }

        // checks priceDriftUpperLimit won't cause pow() call in dataIsValid
        // to exceed max
        if (name == Risk.Parameters.PriceDriftUpperLimit) {
            Oracle.Data memory data = IOverlayV1Feed(feed).latest();
            uint256 _priceDriftUpperLimit = value;
            require(
                _priceDriftUpperLimit * data.macroWindow < MAX_NATURAL_EXPONENT,
                "OVLV1: price drift exceeds max exp"
            );
        }
    }

    /// @notice Caches risk param calculations used in market contract
    /// @notice for gas savings
    function _cacheRiskCalc(Risk.Parameters name, uint256 value) private {
        // caches calculations for dpUpperLimit
        // = e**(priceDriftUpperLimit * data.macroWindow)
        if (name == Risk.Parameters.PriceDriftUpperLimit) {
            Oracle.Data memory data = IOverlayV1Feed(feed).latest();
            uint256 _priceDriftUpperLimit = value;
            uint256 pow = _priceDriftUpperLimit * data.macroWindow;
            dpUpperLimit = EULER.powUp(pow);
        }
    }
}
