import unittest
from overlay_management import OM 

class TestRiskParams(unittest.TestCase):

    def test_risk_param_order(self): #the order is important, so we test it
        risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]
        self.assertListEqual(OM.risk_params, risk_params)

    def test_all_feeds_all_parameters(self):
        afap = OM.get_all_feeds_all_parameters()
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

        deployablelist = [True]
        filtered = OM.filter_by_deployable(deployablelist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 1)
        self.assertEqual(len(filtered['toy-market'].keys()), 1)

        deployablelist = [False]
        filtered = OM.filter_by_deployable(deployablelist)
        self.assertEqual(len(filtered['mcap1000'].keys()), 1)

    def test_feed_network_parameters(self):
        all_feeds_all_parameters= OM.get_feed_network_parameters('mcap1000','arbitrum_goerli','translucent')


if __name__ == '__main__':
    unittest.main()
