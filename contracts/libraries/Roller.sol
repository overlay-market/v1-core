// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

library Roller {
    struct Snapshot {
        uint256 timestamp; // time last snapshot was taken
        uint256 window; // window (length of time) over which will decay
        uint256 accumulator; // accumulator value which will decay over window
        bool isNegative; // whether accumulator value is negative
    }

    /// @dev adjusts accumulator value downward linearly over time.
    /// @dev accumulator should go to zero as one window passes
    function transform(
        Snapshot memory self,
        uint256 timestamp,
        uint256 window,
        uint256 value
    ) internal view returns (Snapshot memory) {
        uint256 dt = timestamp - self.timestamp;
        if (dt >= self.window || self.window == 0) {
            // if one window has passed, prior value has decayed to zero
            return Snapshot({
                timestamp: timestamp,
                window: window,
                accumulator: value,
                isNegative: self.isNegative
            });
        }

        // otherwise, calculate fraction of value remaining given linear decay.
        // fraction of value to take off due to decay (linear drift toward zero)
        // is fraction of windowLast that has elapsed since timestampLast
        self.accumulator -= (self.accumulator * dt) / self.window;

        // add in the new value for accumulator now
        uint256 accumulatorNow = self.accumulator + value;
        if (accumulatorNow == 0) {
            // if accumulator now is zero, windowNow is simply window
            // to avoid 0/0 case below
            return Snapshot({
                timestamp: timestamp,
                window: window,
                accumulator: 0,
                isNegative: self.isNegative
            });
        }

        // recalculate windowNow_ for future decay as a value weighted average time
        // of time left in windowLast for accumulatorLast and window for value
        // vwat = (accumulatorLastWithDecay * (windowLast - dt) + value * window) /
        //        (accumulatorLastWithDecay + value)
        uint256 numerator = self.accumulator * (self.window - dt) + value * window;
        uint256 windowNow = numerator / accumulatorNow;
        return Snapshot({
            timestamp: timestamp,
            window: windowNow,
            accumulator: accumulatorNow,
            isNegative: self.isNegative
        });
    }
}
