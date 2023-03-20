# import all_addresses as aa
import os
import json
from pathlib import Path

#NOTES:
#factory_address refers to OverlayV1Factory
#feed_factory_contract_address refers to XXX

class OM: #Overlay Management


	#TODO fix this hacky way of getting the path	
	RISK_PARAMETERS_DIR = Path(os.getcwd()) / 'scripts/all_feeds_all_parameters.json'   

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
		afap = cls.get_all_feeds_all_parameters()
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
		afap = cls.get_all_feeds_all_parameters()
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
	def filter_by_deployable(cls, selected_deployables: list):
		# this nested for loops are here to explicitly show exactly what is going on 
		afap = cls.get_all_feeds_all_parameters()
		res = {} 
		for market_key, chain_dict in afap.items():
			for chain_key, oracle_dict in chain_dict.items():
				for oracle_key, params in oracle_dict.items():
					if params['deployable'] in selected_deployables:
						if market_key not in res.keys():
							res[market_key] = {}	
						res[market_key].update({chain_key: {oracle_key: params}})
		return res
					

	@classmethod
	def risk_param_array(cls, params):
		return [params[key] for key in cls.risk_params]

	@classmethod
	def get_feed_network_parameters(cls, feed, network, project):
		params = cls.get_all_feeds_all_parameters()
		param = params[feed][network][project]
		aggregator = param['aggregator']
		risk_parameters = param['risk_parameters']
		factory_address = param['factory_address']
		chainlink_feed_factory_contract_address = param['chainlink_feed_factory_contract_address']
		risk_params = cls.risk_param_array(param['risk_parameters'])

		return aggregator, risk_parameters, factory_address, chainlink_feed_factory_contract_address, risk_params


	# XXX THIS IS ACCESS TO THE MAIN DATA STORE XXX
	@classmethod
	def get_all_feeds_all_parameters(cls):

		with  open(cls.RISK_PARAMETERS_DIR, 'r') as f:
			return json.load(f)

	
	# XXX THIS IS ACCESS TO THE MAIN DATA STORE XXX
	@classmethod
	def update_feeds_with_market_parameter(cls, data):

		with  open(cls.RISK_PARAMETERS_DIR, 'w') as f:
			json.dump(data, f, indent=4)
			
