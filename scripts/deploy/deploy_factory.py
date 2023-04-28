from eth_utils import keccak
from ape_safe import ApeSafe
from scripts.overlay_management import OM
from scripts import utils
from brownie import (
    OverlayV1ChainlinkFeedFactory,
    Contract, history,
    accounts, network
)
import json
import web3

def main(chain_id):
    # TODO: This is deprecated and needs to be redone completely
    """
    Deploys a new Feed Factory contract
    """
    all_params = OM.get_all_parameters(chain_id)
    safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])

    create = Contract('0x7cbB62EaA69F79e6873cD1ecB2392971036cFAa4')
    init_code = OverlayV1ChainlinkFeedFactory.bytecode
    tx = create.performCreate(0, init_code, {'from': safe.address})

    feed_factory = OverlayV1ChainlinkFeedFactory.deploy(
        600, 3600, {"from": safe.address})

    factory_addr = OM.const_addresses[chain_id]['factory']
    factory_abi = utils.get_abi(chain_id, factory_addr)
    factory = Contract.from_abi('factory', factory_addr, factory_abi)

    # Add factory
    factory.addFeedFactory(feed_factory, {"from": safe.address})
    safe_tx = safe.multisend_from_receipts()
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)
    breakpoint()
