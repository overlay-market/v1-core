// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

library Roller {
    struct Snapshot {
        uint256 timestamp; // time last snapshot was taken
        uint256 window; // window (length of time) over which will decay
        int256 accumulator; // accumulator value which will decay to zero over window
    }

    /// @dev adjusts accumulator value downward linearly over time.
    /// @dev accumulator should go to zero as one window passes
    function transform(
        Snapshot memory self,
        uint256 timestamp,
        uint256 window,
        int256 value
    ) internal view returns (Snapshot memory) {
        uint256 dt = timestamp - self.timestamp;
        if (dt >= self.window || self.window == 0) {
            // if one window has passed, prior value has decayed to zero
            return Snapshot({timestamp: timestamp, window: window, accumulator: value});
        }

        // otherwise, calculate fraction of value remaining given linear decay.
        // fraction of value to take off due to decay (linear drift toward zero)
        // is fraction of windowLast that has elapsed since timestampLast
        self.accumulator -= (self.accumulator * int256(dt)) / int256(self.window);

        // add in the new value for accumulator now
        int256 accumulatorNow = self.accumulator + value;
        if (accumulatorNow == 0) {
            // if accumulator now is zero, windowNow is simply window
            // to avoid 0/0 case below
            return Snapshot({timestamp: timestamp, window: window, accumulator: 0});
        }

        // recalculate windowNow_ for future decay as a value weighted average time
        // of time left in windowLast for accumulatorLast and window for value
        // vwat = (|accumulatorLastWithDecay| * (windowLast - dt) + |value| * window) /
        //        (|accumulatorLastWithDecay| + |value|)
        // TODO: Use SignedMath in next open zeppelin release 4.5.0
        uint256 w1 = uint256(self.accumulator >= 0 ? self.accumulator : -self.accumulator);
        uint256 w2 = uint256(value >= 0 ? value : -value);
        uint256 windowNow = (w1 * (self.window - dt) + w2 * window) / (w1 + w2);
        return Snapshot({timestamp: timestamp, window: windowNow, accumulator: accumulatorNow});
    }
}
