import all_addresses as aa

#NOTES:
#factory_address refers to OverlayV1Factory
#feed_factory_contract_address refers to XXX

class OM: #Overlay Management

	#CHAINS:
	ETH_MAIN = 'ethereum_goerli'
	ETH_TEST = 'ethereum_mainnet'
	ARB_TEST = 'arbitrum_goerli'
	ARB_MAIN = 'arbitrum_one'

    ## XXX these are ordered!!! XXX DO NOT CHANGE
	risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]

	@classmethod
	def filter_by_blockchain(cls, selected_chains: list):
		# this nested for loops are here to explicitly show exactly what is going on 
		afap = cls.all_feeds_all_parameters
		res = {} 
		for market_key, chain_dict in afap.items():
			for chain_key, oracle_dict in chain_dict.items():
				if chain_key in selected_chains:
					if market_key not in res.keys():
						res[market_key] = {}
					for oracle_key, params in oracle_dict.items():					
						res[market_key].update({chain_key: {oracle_key: params}})

		return res

	@classmethod
	def filter_by_oracle(cls, selected_oracles: list):
		# this nested for loops are here to explicitly show exactly what is going on 
		afap = cls.all_feeds_all_parameters
		res = {} 
		for market_key, chain_dict in afap.items():
			for chain_key, oracle_dict in chain_dict.items():
				for oracle_key, params in oracle_dict.items():
					if oracle_key in selected_oracles:
						if market_key in res.keys():
							res[market_key].update({chain_key: {oracle_key: params}})
						else:
							res[market_key] = {}
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
	@property
	def all_feeds_all_parameters():
		...