# import all_addresses as aa
import os
import json
from pathlib import Path

#NOTES:
#factory_address refers to OverlayV1Factory
#feed_factory_contract_address refers to XXX

class OM: #Overlay Management


	#TODO fix this hacky way of getting the path	
	RISK_PARAMETERS_DIR = Path(os.getcwd()) / 'scripts/all_parameters.json'   

	#CHAINS:
	ETH_MAIN = 'ethereum_mainnet'
	ETH_TEST = 'ethereum_goerli'
	ARB_TEST = 'arbitrum_goerli'
	ARB_MAIN = 'arbitrum_one'
	FEED_ADDRESS = 'feed_address'
	MARKET_ADDRESS = 'market_address'
	DEPLOYED_MARKET = 'deployed_market'

	#CONSTANT ADDRESSES (CHAIN WISE):
	const_addresses = {
		ARB_MAIN: {
			'factory': '0xC3cB99652111e7828f38544E3e94c714D8F9a51a',
			'state': '0xC3cB99652111e7828f38544E3e94c714D8F9a51a',
			'ovl': '0x4305C4Bc521B052F17d389c2Fe9d37caBeB70d54',
			'feed_factory': {
				'chainlink': '0x92ee7A26Dbc18E9C0157831d79C2906A02fD1FAe',
				'nftperp': '0xFA0282158936D8A9cC9F413A90d592a47397239a',
				'uniswap_v3': '0x37cFe8B998205aA38b1aFDA48706551EF6EBc1aE'
			}
		},

		ETH_MAIN: {
			'factory': '0x9a74758c2A80fA1B1d899E0E1f24CF505a4Dea33',
			'state': '0x477122219aa1F76E190f480a85af97DE0A643320',
			'ovl': '0xdc77acc82cce1cc095cba197474cc06824ade6f7',
			'feed_factory': {
				'uniswap_v3': '0x40a9C6E8d60bE1CE297Bef6a9aC3337d45193D87'
			}
		},

		ARB_TEST: {
			'factory': '0x733A47039C02bB3B5950F1c6DAaC5E24f3821AB2',
			'state': '0x68eb0F1Fbbb35b98526F53c01B18507f95F02119',
			'ovl': '0x1023b1BC47b9b449eAD9329EE0eFD4fDAcA3D767',
			'feed_factory': {
				'chainlink': '0x75D6b2D432EeB742942E4f6E9FF77Db56B834099'
			}
		},

		ETH_TEST: {
			'factory': '0x2422d0108b844FC5114E864346c584b0d10d57C0',
			'state': '0x9d2fbD680e2873A99dFc1dB876e933c7CE05Cf12',
			'ovl': '0xdBD4a09ac1962F028390C53F4a4d126F5E13baEe',
			'feed_factory': {
				'chainlink': '0x5967A38B49ad2B63A5f04D02dbEAaD76BC4965Ac'
			}
		}
	}

    ## XXX these are ordered!!! XXX DO NOT CHANGE 
	risk_params = ["k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage", "circuitBreakerWindow", "circuitBreakerMintTarget", "maintenanceMarginFraction", "maintenanceMarginBurnRate", "liquidationFeeRate", "tradingFeeRate", "minCollateral", "priceDriftUpperLimit", "averageBlockTime"]

	@classmethod
	def get_deployable(cls, chain_id, contract_type):
		'''
		Get deployable contracts.
		Deployable contracts might be of the follring types:
		feed_factory, feed or market
		'''
		all_params = cls.get_all_parameters(chain_id)
		deployable_contracts = []
		for market_key, market_dict in all_params.items():
			if market_dict[f'{contract_type}_parameters']['deployable']:
				deployable_contracts.append(market_key)
		return deployable_contracts
	
	
	# @classmethod
	# def filter_by_blockchain(cls, selected_chains: list, to_filter: dict = None):
	# 	# this nested for loops are here to explicitly show exactly what is going on 
	# 	all_params = to_filter if to_filter else cls.get_all_parameters()
	# 	res = {} 
	# 	for market_key, chain_dict in all_params.items():
	# 		for chain_key, oracle_dict in chain_dict.items():
	# 			if chain_key in selected_chains:
	# 				if market_key not in res.keys():
	# 					res[market_key] = {}
	# 				for oracle_key, params in oracle_dict.items():					
	# 					res[market_key].update({chain_key: {oracle_key: params}})

	# 	return res

	# @classmethod
	# def filter_by_oracle(cls, selected_oracles: list, to_filter: dict = None):
	# 	# this nested for loops are here to explicitly show exactly what is going on 
	# 	all_params = to_filter if to_filter else cls.get_all_parameters()
	# 	res = {} 
	# 	for market_key, chain_dict in all_params.items():
	# 		for chain_key, oracle_dict in chain_dict.items():
	# 			for oracle_key, params in oracle_dict.items():
	# 				if oracle_key in selected_oracles:
	# 					if market_key not in res.keys():
	# 						res[market_key] = {}
	# 					res[market_key].update({chain_key: {oracle_key: params}})
	# 	return res
	
	# @classmethod
	# def filter_by_deployable(cls, to_filter: dict = None):
	# 	# this nested for loops are here to explicitly show exactly what is going on 
	# 	all_params = to_filter if to_filter else cls.get_all_parameters()
	# 	res = {} 
	# 	for market_key, chain_dict in all_params.items():
	# 		for chain_key, oracle_dict in chain_dict.items():
	# 			for oracle_key, params in oracle_dict.items():
	# 				if params['deployable']:
	# 					if market_key not in res.keys():
	# 						res[market_key] = {}	
	# 					res[market_key].update({chain_key: {oracle_key: params}})
	# 	return res
					

	@classmethod
	def risk_param_array(cls, params):
		return [params[key] for key in cls.risk_params]

	# @classmethod
	# def get_market_parameters(cls, feed, network, oracle):
	# 	params = cls.get_all_parameters()[feed][network][oracle]
	# 	aggregator = params['aggregator']
	# 	risk_parameters = params['risk_parameters']
	# 	factory_address = params['factory_address']
	# 	#TODO fix the next line
	# 	chainlink_feed_factory_contract_address = params['chainlink_feed_factory_contract_address']
	# 	risk_params = cls.risk_param_array(params['risk_parameters'])

	# 	return aggregator, risk_parameters, factory_address, chainlink_feed_factory_contract_address, risk_params


	# XXX THIS IS ACCESS TO THE MAIN DATA STORE XXX
	@classmethod
	def get_all_parameters(cls, chain_id: str = None):
		'''
		Return all parameters of all chains if no chain_id is specified.
		Otherwise return all parameters of specified chain_id only.
		'''
		with  open(cls.RISK_PARAMETERS_DIR, 'r') as f:
			all_params = json.load(f)
		if chain_id is None:
			return all_params
		else:
			return all_params[chain_id]

	@classmethod
	def update_all_parameters(cls, data, chain_id):
		all_params = cls.get_all_parameters()
		all_params[chain_id] = data
		with  open(cls.RISK_PARAMETERS_DIR, 'w') as f:
			json.dump(all_params, f, indent=4)
