import unittest
from all_feeds_all_parameters import AllFeedsAllParameters

class TestRiskParams(unittest.TestCase):

    def test_risk_param_order(self): #the order is important, so we test it
        risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]
        afap = AllFeedsAllParameters
        self.assertListEqual(afap.risk_params, risk_params)

    def test_filter_by_network(self):
        afap = AllFeedsAllParameters

        chainlist = [afap.ARB_TEST, afap.ARB_MAIN]
        filtered = afap.filter_by_blockchain(chainlist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 2)

        chainlist = [afap.ARB_TEST]
        filtered = afap.filter_by_blockchain(chainlist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 1)



if __name__ == '__main__':
    unittest.main()
