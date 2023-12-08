import unittest
from unittest.mock import mock_open, patch
import json
from overlay_management import OM


class TestOM(unittest.TestCase):

    mock_data = '''
        {
            "arbitrum_goerli": {
                "market1": {
                    "oracle": "mock_oracle",
                    "feed_parameters": {
                        "deployable": true,
                        "aggregator": "mock_aggregator"
                        },
                    "risk_parameter": {
                        "deployable": false,
                        "k": 123
                    }
                }
            }
        }
    '''

    def get_mock_dict(self):
        return json.loads(self.mock_data)

    def test_risk_param_order(self):  # The order is important, so we test it
        risk_params = [
            "k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage",
            "circuitBreakerWindow", "circuitBreakerMintTarget",
            "maintenanceMarginFraction", "maintenanceMarginBurnRate",
            "liquidationFeeRate", "tradingFeeRate", "minCollateral",
            "priceDriftUpperLimit", "averageBlockTime"
        ]
        self.assertListEqual(OM.risk_params, risk_params)

    @patch("overlay_management.open", mock_open(read_data=mock_data))
    def test_get_all_parameters(self):
        # Test with chain_id as input
        result = OM.get_all_parameters("arbitrum_goerli")
        expected_result = self.get_mock_dict()["arbitrum_goerli"]
        self.assertEqual(result, expected_result)

        # Test with no input
        result = OM.get_all_parameters()
        expected_result = self.get_mock_dict()
        self.assertEqual(result, expected_result)

    @patch("overlay_management.open", mock_open(read_data=mock_data))
    def test_update_all_parameters(self):
        # Update the parameters for the "arbitrum_goerli" chain
        new_params = {
            "market1": {
                "oracle": "new_mock_oracle",
                "feed_parameters": {
                    "deployable": False,
                    "aggregator": "new_mock_aggregator"
                },
                "risk_parameter": {
                    "deployable": True,
                    "k": 456
                }
            }
        }
        OM.update_all_parameters(new_params, "arbitrum_goerli")

        # Verify that the updated parameters were stored
        expected_result = self.get_mock_dict()
        expected_result["arbitrum_goerli"]["market1"] = new_params["market1"]
        with patch("overlay_management.open",
                   mock_open(read_data=json.dumps(expected_result))):
            result = OM.get_all_parameters("arbitrum_goerli")
            self.assertEqual(result, new_params)


if __name__ == '__main__':
    unittest.main()
