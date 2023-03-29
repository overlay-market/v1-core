import unittest
from overlay_management import OM 

class TestRiskParams(unittest.TestCase):

    def test_risk_param_order(self): #the order is important, so we test it
        risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]
        self.assertListEqual(OM.risk_params, risk_params)

    def test_all_feeds_all_parameters(self):
        ap = OM.get_all_parameters()
        ...

    def test_filter_by_network(self):
        chainlist = [OM.ARB_TEST, OM.ARB_MAIN]
        filtered = OM.filter_by_blockchain(chainlist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 2)

        chainlist = [OM.ARB_TEST]
        filtered = OM.filter_by_blockchain(chainlist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 1)

    def test_filter_by_oracle(self):
        oraclelist = ['translucent']
        filtered = OM.filter_by_oracle(oraclelist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 2)

        oraclelist = ['translucent']
        filtered = OM.filter_by_oracle(oraclelist)
        self.assertEqual(len(filtered['toy-market'].keys()), 1)

    def test_filter_by_deployable(self):
        all_params = OM.get_all_parameters()
        filtered = OM.filter_by_deployable(all_params)
        self.assertEqual(len(filtered['mcap1000'].keys()), 1)
        self.assertEqual(len(filtered['toy-market'].keys()), 1)

    def test_get_market_parameters(self):
        market_parameters = OM.get_market_parameters('mcap1000','arbitrum_goerli','translucent')
        all_params = OM.get_all_parameters()
        params = all_params['mcap1000']['arbitrum_goerli']['translucent']['aggregator']
        self.assertEqual(market_parameters[0], params)


if __name__ == '__main__':
    unittest.main()
 