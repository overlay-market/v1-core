#NOTES:
#factory_address refers to OverlayV1Factory
#feed_factory_contract_address refers to XXX

class AllFeedsAllParameters:

	#CHAINS:
	ETH_MAIN = 'ethereum_goerli'
	ETH_TEST = 'ethereum_mainnet'
	ARB_TEST = 'arbitrum_goerli'
	ARB_MAIN = 'arbitrum_one'

    ## XXX these are ordered!!! XXX DO NOT CHANGE
	risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]

	@classmethod
	def filter_by_blockchain(cls, selected_chains: list):
		afap = cls.all_feeds_all_parameters
		res = {} 
		for market, chain in afap.items():
			for chain, oracle in chain.items():
				if chain in selected_chains:
					if market not in res.keys():
						res[market] = {}
					for oracle, params in oracle.items():					
						res[market].update({chain: {oracle: params}})

		return res

	@classmethod
	def filter_by_oracle(cls, selected_oracles: list):
		afap = cls.all_feeds_all_parameters
		res = {} 
		for market, chain in afap.items():
			for chain, oracle in chain.items():
				for oracle, params in oracle.items():
					if oracle in selected_oracles:
						if market in res.keys():
							res[market].update({chain: {oracle: params}})
						else:
							res[market] = {chain: {oracle: params}}
		return res
					

	@classmethod
	def risk_param_array(cls, params):
		return [params[key] for key in cls.risk_params]

	@classmethod
	def get_feed_network_parameters(cls, feed, network):
		params = cls.all_feeds_all_parameters[feed][network]
		aggregator = params['aggregator']
		risk_parameters = params['risk_parameters']
		factory_address = params['factory_address']
		chainlink_feed_factory_contract_address = params['chainlink_feed_factory_contract_address']
		risk_params = cls.risk_param_array(params['risk_parameters'])

		return aggregator, risk_parameters, factory_address, chainlink_feed_factory_contract_address, risk_params


	# XXX THIS IS THE MAIN DATA STORE XXX
	all_feeds_all_parameters = {
		"mcap1000" :  {
			"arbitrum_goerli" : {
				"translucent": {
					"macroWindow" : 3600,
					"microWindow" : 600,
					"aggregator"  : "0x2748A42aBd328835DFDA748bdD1D77Ce3c3312EE",
					"factory_address" : "0x6eD5CCC86F24AA307dee58d4630d97F2f660C38A",
					"chainlink_feed_factory_contract_address" : "0x5121C75e7cADE920B32FeCf230600654F73ee73C",
					"risk_parameters": {
						"k": 115740740741,
						"lambda": 613091000000000000,
						"delta": 3510000000000000,
						"capPayoff": 10000000000000000000,
						"capNotional": 800000000000000000000000,
						"capLeverage": 5000000000000000000,
						"circuitBreakerWindow": 2592000,
						"circuitBreakerMintTarget": 66670000000000000000000,
						"maintenanceMarginFraction": 57790000000000000,
						"maintenanceMarginBurnRate": 52968000000000000,
						"liquidationFeeRate": 50000000000000000,
						"tradingFeeRate": 750000000000000,
						"minCollateral": 100000000000000,
						"priceDriftUpperLimit": 100000000000000,
						"averageBlockTime": 0
						}
					}
				},
			"arbitrum_one" : {
				"translucent": {
					"macroWindow" : 3600,
					"microWindow" : 600,
					"aggregator"  : "0x2748A42aBd328835DFDA748bdD1D77Ce3c3312EE",
					"factory_address" : "0x6eD5CCC86F24AA307dee58d4630d97F2f660C38A",
					"chainlink_feed_factory_contract_address" : "0x5121C75e7cADE920B32FeCf230600654F73ee73C",
					"risk_parameters": {
						"k": 115740740741,
						"lambda": 613091000000000000,
						"delta": 3510000000000000,
						"capPayoff": 10000000000000000000,
						"capNotional": 800000000000000000000000,
						"capLeverage": 5000000000000000000,
						"circuitBreakerWindow": 2592000,
						"circuitBreakerMintTarget": 66670000000000000000000,
						"maintenanceMarginFraction": 57790000000000000,
						"maintenanceMarginBurnRate": 52968000000000000,
						"liquidationFeeRate": 50000000000000000,
						"tradingFeeRate": 750000000000000,
						"minCollateral": 100000000000000,
						"priceDriftUpperLimit": 100000000000000,
						"averageBlockTime": 0
						}
					}
				},
			},

			# TODELETE toy example for testing
			"toy-market": {
			"arbitrum_goerli" : {
				"macroWindow" : 3600,
				"microWindow" : 600,
				"aggregator"  : "0x2748A42aBd328835DFDA748bdD1D77Ce3c3312EE",
				"factory_address" : "0x6eD5CCC86F24AA307dee58d4630d97F2f660C38A",
				"chainlink_feed_factory_contract_address" : "0x5121C75e7cADE920B32FeCf230600654F73ee73C",
				"risk_parameters": {
					"k": 115740740741,
					"lambda": 613091000000000000,
					"delta": 3510000000000000,
					"capPayoff": 10000000000000000000,
					"capNotional": 800000000000000000000000,
					"capLeverage": 5000000000000000000,
					"circuitBreakerWindow": 2592000,
					"circuitBreakerMintTarget": 66670000000000000000000,
					"maintenanceMarginFraction": 57790000000000000,
					"maintenanceMarginBurnRate": 52968000000000000,
					"liquidationFeeRate": 50000000000000000,
					"tradingFeeRate": 750000000000000,
					"minCollateral": 100000000000000,
					"priceDriftUpperLimit": 100000000000000,
					"averageBlockTime": 0
					}
				}
			}
		}
