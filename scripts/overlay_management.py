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

	#CONSTANT ADDRESSES (CHAIN WISE):
	const_addresses = {
		'arbitrum_one': {
			'factory': '0xC3cB99652111e7828f38544E3e94c714D8F9a51a',
			'state': '0xC3cB99652111e7828f38544E3e94c714D8F9a51a',
			'ovl': '0x4305C4Bc521B052F17d389c2Fe9d37caBeB70d54'
		},

		'ethereum_mainnet_addresses': {
			'factory': '0x9a74758c2A80fA1B1d899E0E1f24CF505a4Dea33',
			'state': '0x477122219aa1F76E190f480a85af97DE0A643320',
			'ovl': '0xdc77acc82cce1cc095cba197474cc06824ade6f7'
		},

		'arbitrum_goerli': {
			'factory': '0x733A47039C02bB3B5950F1c6DAaC5E24f3821AB2',
			'state': '0x68eb0F1Fbbb35b98526F53c01B18507f95F02119',
			'ovl': '0x1023b1BC47b9b449eAD9329EE0eFD4fDAcA3D767'
		},
	}

    ## XXX these are ordered!!! XXX DO NOT CHANGE 
	risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]

	@classmethod
	def filter_by_blockchain(cls, selected_chains: list, to_filter: dict = None):
		# this nested for loops are here to explicitly show exactly what is going on 
		afap = to_filter if to_filter else cls.get_all_feeds_all_parameters()
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
	def filter_by_oracle(cls, selected_oracles: list, to_filter: dict = None):
		# this nested for loops are here to explicitly show exactly what is going on 
		afap = to_filter if to_filter else cls.get_all_feeds_all_parameters()
		res = {} 
		for market_key, chain_dict in afap.items():
			for chain_key, oracle_dict in chain_dict.items():
				for oracle_key, params in oracle_dict.items():
					if oracle_key in selected_oracles:
						if market_key not in res.keys():
							res[market_key] = {}
						res[market_key].update({chain_key: {oracle_key: params}})
		return res
	
	@classmethod
	def filter_by_deployable(cls, to_filter: dict = None):
		# this nested for loops are here to explicitly show exactly what is going on 
		afap = to_filter if to_filter else cls.get_all_feeds_all_parameters()
		res = {} 
		for market_key, chain_dict in afap.items():
			for chain_key, oracle_dict in chain_dict.items():
				for oracle_key, params in oracle_dict.items():
					if params['deployable']:
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

	@classmethod
	def getKey(cls, chain_dict):
		for key in chain_dict:
			return key
			
