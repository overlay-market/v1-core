import unittest
from all_feeds_all_parameters import AllFeedsAllParameters

class TestRiskParams(unittest.TestCase):

    def test_risk_param_order(self): #the order is important, so we test it
        risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]
        afap = AllFeedsAllParameters
        self.assertListEqual(afap.risk_params, risk_params)

        ...

if __name__ == '__main__':
    unittest.main()
