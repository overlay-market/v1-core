# import all_addresses as aa
import os
import json
from pathlib import Path
from brownie import network


class OM:  # Overlay Management

    RISK_PARAMETERS_DIR = Path(os.getcwd()) / 'scripts/all_parameters.json'

    # CHAINS:
    ETH_MAIN = 'ethereum_mainnet'
    ETH_TEST = 'ethereum_goerli'
    ARB_TEST = 'arbitrum_goerli'
    ARB_MAIN = 'arbitrum_one'

    # CHAIN IDs: BROWNIE NETWORKS
    NETWORK_MAPPING = {
        ETH_MAIN: 'mainnet',
        ETH_TEST: 'goerli',
        ARB_MAIN: 'arbitrum-main',
        ARB_TEST: 'arbitrum-goerli'
    }

    # SAFES
    PROTOCOL_SAFE = 'protocol_safe'

    # ADDRESSES
    FACTORY_ADDRESS = 'factory'
    STATE_ADDRESS = 'state'
    OVL_ADDRESS = 'ovl'
    CREATE_CALL = 'create_call'
    FEED_FACTORY_ADDRESS = 'feed_factory'
    CHAINLINK_FEED_FACTORY_ADDRESS = 'OverlayV1ChainlinkFeedFactory'
    NFTPERP_FEED_FACTORY_ADDRESS = 'nftperp'
    UNI_V3_FEED_FACTORY_ADDRESS = 'uniswap_v3'
    # CONSTANT ADDRESSES (CHAIN WISE):
    const_addresses = {
        ARB_MAIN: {
            PROTOCOL_SAFE: '0x5985FD48b48fdde2C5c1BC0b4f591c83D961184B',
            FACTORY_ADDRESS: '0xFA39CdE07Ff63b4329A70784C0600Da38CF4777C',
            STATE_ADDRESS: '0xC3cB99652111e7828f38544E3e94c714D8F9a51a',
            OVL_ADDRESS: '0x4305C4Bc521B052F17d389c2Fe9d37caBeB70d54'
        },
        ETH_MAIN: {
            PROTOCOL_SAFE: '0xB635D8EcC59330dDf611B4aA02e9d78820Cd3985',
            FACTORY_ADDRESS: '0x9a74758c2A80fA1B1d899E0E1f24CF505a4Dea33',
            STATE_ADDRESS: '0x477122219aa1F76E190f480a85af97DE0A643320',
            OVL_ADDRESS: '0xdc77acc82cce1cc095cba197474cc06824ade6f7'
        },
        ARB_TEST: {
            FACTORY_ADDRESS: '0x733A47039C02bB3B5950F1c6DAaC5E24f3821AB2',
            STATE_ADDRESS: '0x68eb0F1Fbbb35b98526F53c01B18507f95F02119',
            OVL_ADDRESS: '0x1023b1BC47b9b449eAD9329EE0eFD4fDAcA3D767'
        },
        ETH_TEST: {
            PROTOCOL_SAFE: '0x5ce44FF0C50f6a28f75932b8b12c5cbE9dEc343E',
            FACTORY_ADDRESS: '0x2422d0108b844FC5114E864346c584b0d10d57C0',
            STATE_ADDRESS: '0x9d2fbD680e2873A99dFc1dB876e933c7CE05Cf12',
            OVL_ADDRESS: '0xdBD4a09ac1962F028390C53F4a4d126F5E13baEe',
            CREATE_CALL: '0x7cbB62EaA69F79e6873cD1ecB2392971036cFAa4'
        }
    }
    # XXX these are ordered!!! XXX DO NOT CHANGE
    risk_params = [
        "k", "lambda", "delta", "capPayoff", "capNotional", "capLeverage",
        "circuitBreakerWindow", "circuitBreakerMintTarget",
        "maintenanceMarginFraction", "maintenanceMarginBurnRate",
        "liquidationFeeRate", "tradingFeeRate", "minCollateral",
        "priceDriftUpperLimit", "averageBlockTime"]

    @classmethod
    def get_deployable_feed_market(cls, chain_id, contract_type):
        '''
        Get deployable feed or market
        '''
        all_params = cls.get_all_parameters(chain_id)
        deployable_contracts = []
        for ff_key, ff_dict in all_params.items():
            if 'feed_factory_address' not in ff_dict:
                print(f"Skipping all markets and feeds in {ff_key} "
                      "since feed factory is not deployed")
                continue
            else:
                for market_key, market_dict in ff_dict['markets'].items():
                    if f"{contract_type}_address" not in market_dict:
                        dc = {ff_key: market_key}
                        deployable_contracts.append(dc)
        return deployable_contracts

    @classmethod
    def get_deployable_feed_factory(cls, chain_id):
        '''
        Get deployable feed factories
        '''
        all_params = cls.get_all_parameters(chain_id)
        deployable_ff = []
        for ff in all_params.items():
            if 'feed_factory_address' not in ff[1].keys():
                deployable_ff.append(ff[0])
        return deployable_ff

    @classmethod
    def risk_param_array(cls, params):
        return [params[key] for key in cls.risk_params]
    # XXX THIS IS ACCESS TO THE MAIN DATA STORE XXX

    @classmethod
    def get_all_parameters(cls, chain_id: str = None):
        '''
        Return all parameters of all chains if no chain_id is specified.
        Otherwise return all parameters of specified chain_id only.
        '''
        with open(cls.RISK_PARAMETERS_DIR, 'r') as f:
            all_params = json.load(f)
        if chain_id is None:
            return all_params
        else:
            return all_params[chain_id]

    @classmethod
    def update_all_parameters(cls, data, chain_id):
        all_params = cls.get_all_parameters()
        all_params[chain_id] = data
        with open(cls.RISK_PARAMETERS_DIR, 'w') as f:
            json.dump(all_params, f, indent=4)

    @classmethod
    def connect_to_chain(cls, chain_id):
        '''
        Connect to chain that corresponds to chain_id
        '''
        # Disconnect from default network (mainnet-fork)
        network.disconnect()
        # Connect to right network
        if chain_id == cls.ARB_TEST:
            # For deploying on arbitrum testnet; ape-safe isn't used.
            # So, we don't need to connect to a the forked chain.
            network.connect(cls.NETWORK_MAPPING[chain_id])
        else:
            # For all other chains, we need to connect to a forked chain to
            # deploy contracts using ape-safe.
            network.connect(f'{cls.NETWORK_MAPPING[chain_id]}-fork')
        print(f"You are using the '{network.show_active()}' network")
