from ape_safe import ApeSafe
from brownie import network, Contract, history
from scripts.overlay_management import OM
from scripts import utils

# Add feed factory addresses that need to be removed
FEED_FACTORY_ADDRS = ['0xce60444eca6695a00c8343441e48cbc043be4ab2']


def main(chain_id):
    print(f"You are using the '{network.show_active()}' network")
    safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
    factory = utils.load_const_contract(chain_id, OM.FACTORY_ADDRESS)
    for feed_factory_addr in FEED_FACTORY_ADDRS:
        tx = factory.removeFeedFactory(
            feed_factory_addr,
            {'from': safe.address}
        )

    # Sign and post
    hist = history.from_sender(safe.address)
    safe_tx = safe.multisend_from_receipts(hist[-len(FEED_FACTORY_ADDRS):])
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)